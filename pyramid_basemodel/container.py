# -*- coding: utf-8 -*-

"""Base model container.

Provides a base model container, used by the Pyramid traversal
machinery and a mixin to aid with traversal from an instance
back up the tree.
"""

__all__ = [
    "BaseModelContainer",
    "InstanceTraversalMixin",
]

import logging
import re
from collections.abc import Callable
from typing import Any, ClassVar, cast

from pyramid.interfaces import ILocation
from pyramid.request import Request
from pyramid.security import ALL_PERMISSIONS, Allow, Authenticated, Deny, Everyone
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Query, scoped_session
from sqlalchemy.orm.scoping import QueryPropertyDescriptor
from zope.interface import alsoProvides, implementer

from pyramid_basemodel import BaseMixin, Session
from pyramid_basemodel.interfaces import IModelContainer
from pyramid_basemodel.root import BaseRoot

valid_slug = re.compile(r"^[.\w-]{1,64}$", re.U)
logger = logging.getLogger(__name__)

#: Signature shared by ``slug_validator`` and any user supplied replacement.
Validator = Callable[..., None]


def slug_validator(node: Any, value: str, regexp: re.Pattern[str] = valid_slug) -> None:
    """Validate slug.

    Defaults to using a slug regexp.
    """
    # Raise a ValueError.
    if not regexp.match(value):
        raise ValueError(f"{value} is not a valid slug.")


@implementer(IModelContainer)
class BaseModelContainer(BaseRoot):
    """Traversal factory that looks up model classes by property."""

    property_name: str = "slug"
    validation_exception: ClassVar[type[BaseException]] = Exception

    #: Either ``self._validator`` or the ``validator`` passed to ``__init__``.
    validator: Validator

    @property
    def _validator(self) -> Validator:
        return slug_validator

    # Default container acl to be private whilst granting authenticated
    # users create permission.
    __acl__: ClassVar[list[tuple[Any, ...]]] = [
        (Allow, "r:admin", ALL_PERMISSIONS),
        (Allow, Authenticated, "view"),
        (Allow, Authenticated, "create"),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]

    @property
    def name(self) -> str:
        """Return plurar version of a class name."""
        return self.model_cls.plural_class_name

    @property
    def class_name(self) -> str:
        """Determine class name based on the _class_name or the __tablename__."""
        return self.model_cls.class_name

    @property
    def plural_class_name(self) -> str:
        """Return plurar version of a class name."""
        return self.model_cls.plural_class_name

    @property
    def class_slug(self) -> str:
        """Class slug based on either _class_slug or __tablename__."""
        return self.model_cls.class_slug

    def get_child(self, key: str) -> Any:
        """Query for and return the child instance, if found."""
        column = getattr(self.model_cls, self.property_name)
        query = self.model_cls.query.filter(column == key)
        return query.first()

    def __getitem__(self, key: str) -> Any:
        """Lookup model instance by key."""
        try:
            self.validator(None, key)
        except self.validation_exception:
            raise KeyError(key)

        context = self.get_child(key)
        if not context:
            raise KeyError(key)

        return self.locatable(context, key)

    def __init__(
        self,
        request: Request | None,
        model_cls: type["BaseMixin"],
        key: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        """Instantiate the container."""
        # Compose.
        if key is None:
            key = model_cls.class_slug
        if parent is None:
            parent = BaseRoot(request)

        self.request = request
        self.model_cls = model_cls
        self.__name__ = key
        self.__parent__ = parent
        if "property_name" in kwargs:
            self.property_name = kwargs["property_name"]
        if "validator" in kwargs:
            self.validator = kwargs["validator"]
        else:
            self.validator = self._validator


class InstanceTraversalMixin:
    """Provide a default __parent__ implementation for traversal."""

    request: Request | None = None
    traversal_key_name: str = "slug"
    validation_exception: ClassVar[type[BaseException]] = Exception

    #: Provided by ``BaseMixin`` when the two are combined on a model.
    query: ClassVar[QueryPropertyDescriptor]

    #: Set by ``locatable`` once the instance has been located.
    _located_parent: Any

    @property
    def _validator(self) -> Validator:
        return slug_validator

    @property
    def _base_child_query(self) -> Query[Any]:
        return self.query

    def get_container(self) -> Any:
        """Reverse up the parent traversal hierarchy until reaching a container."""
        target: Any = self
        while True:
            parent = target.__parent__
            if not parent:
                return None
            if IModelContainer.providedBy(parent):
                return parent
            target = parent

    def locatable(self, context: Any, key: str, provides: Callable[..., None] = alsoProvides) -> Any:
        """Make a context object locatable and pass on the request."""
        if not hasattr(context, "__name__"):
            context.__name__ = key
        context._located_parent = self
        context.request = self.request
        if not ILocation.providedBy(context):
            provides(context, ILocation)
        return context

    @property
    def __parent__(
        self,
        container_cls: type[BaseModelContainer] = BaseModelContainer,
        session: scoped_session[Any] = Session,
    ) -> Any:
        """Either return ``self.parent``, or a model container object."""
        # If the context has been located, return the container.
        if hasattr(self, "_located_parent"):
            return self._located_parent

        # Add self to the session to avoid ``DetachedInstanceError``s.
        session.add(self)

        # If the model has a parent, return it.
        parent = getattr(self, "parent", None)
        if parent:
            return parent

        # Otherwise instantiate a "fake" traversal container and return that.
        # It's "fake" because it doesn't know about it's parent and doesn't
        # have a copy of the request.
        # This mixin is only usable on a model that also mixes in ``BaseMixin``.
        container = container_cls(None, cast("type[BaseMixin]", self.__class__))
        return container

    def __getitem__(self, key: str) -> Any:
        """Lookup model instance by key."""
        try:
            self._validator(None, key)
        except self.validation_exception:
            raise KeyError(key)

        # Only lookup children from instances that have them.
        has_children = hasattr(self, "children")
        if not has_children:
            raise KeyError(key)

        # Only lookup if the target column exists.
        column = getattr(self.__class__, self.traversal_key_name, None)
        if not column:
            raise KeyError(key)

        try:
            query = self._base_child_query
            query = query.filter_by(parent=self).filter(column == key)
            context = query.first()
            if not context:
                raise KeyError(key)
        except InvalidRequestError as err:
            # If the query was invalid, the lookup fails, e.g.: if the
            # instance had the requisit properties but they weren't actually
            # sqlalchemy columns.
            logger.warning(err, exc_info=True)
            raise KeyError(key)

        # Return the context, having set the parent and flagged as locatable.
        return self.locatable(context, key)
