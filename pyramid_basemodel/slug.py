# -*- coding: utf-8 -*-

"""Provides a base ORM mixin for models that need a name and a url slug."""

__all__ = [
    "BaseSlugNameMixin",
]

import logging
from collections.abc import Callable
from typing import Any, ClassVar

import slugify
from sqlalchemy import exc as sa_exc
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, scoped_session
from sqlalchemy.orm.scoping import QueryPropertyDescriptor
from sqlalchemy.types import Unicode

from pyramid_basemodel import Session
from pyramid_basemodel.util import ensure_unique, generate_random_digest

logger = logging.getLogger(__name__)


class BaseSlugNameMixin:
    """Base mixin delivering a slug functionality.

    ORM mixin class that provides ``slug`` and ``name`` properties, with a
    ``set_slug`` method to set the slug value from the name and a default
    name aware factory classmethod.
    """

    _max_slug_length: ClassVar[int] = 64
    _slug_is_unique: ClassVar[bool] = True

    #: Provided by ``BaseMixin`` when the two are combined on a model.
    query: ClassVar[QueryPropertyDescriptor]

    @property
    def __name__(self) -> str:
        """Url friendly name."""
        return self.slug

    @declared_attr
    def slug(cls) -> Mapped[str]:
        """Get url friendly slug, e.g.: `foo-bar`."""
        return mapped_column(Unicode(cls._max_slug_length), nullable=False, unique=cls._slug_is_unique)

    @declared_attr
    def name(cls) -> Mapped[str]:
        """Get human readable name, e.g.: `Foo Bar`."""
        return mapped_column(Unicode(cls._max_slug_length), nullable=False)

    def set_slug(
        self,
        candidate: str | None = None,
        gen_digest: Callable[..., str] = generate_random_digest,
        inspect: Callable[[Any], Any] = sa_inspect,
        session: scoped_session[Any] = Session,
        to_slug: Callable[..., str] = slugify.slugify,
        unique: Callable[..., str] = ensure_unique,
    ) -> None:
        """Generate and set a unique ``self.slug`` from ``self.name``.

        :param get_digest: function to generate random digest. Used of there's no name set.
        :param inspect:
        :param session: SQLAlchemy's session
        :param to_slug: slugify function
        :param unique: unique function
        """
        # Generate a candidate slug.
        if candidate is None:
            if self.name:
                candidate = to_slug(self.name)
            if not candidate:
                candidate = gen_digest(num_bytes=16)

        # Make sure it's not longer than 64 chars.
        length = self._max_slug_length
        length_minus_ellipsis = length - 3
        candidate = candidate[:length]
        unique_candidate = candidate[:length_minus_ellipsis]

        # If there's no name, only set the slug if its not already set.
        if self.slug and not self.name:
            return

        # If there is a name and the slug matches it, then don't try and
        # reset (i.e.: we only want to set a slug if the name has changed).
        if self.slug and self.name:
            if self.slug == candidate:
                # XXX as long as the instance is pending, as otherwise
                # we skip checking uniqueness on unsaved instances.
                try:
                    insp = inspect(self)
                except sa_exc.NoInspectionAvailable:
                    pass
                else:
                    if insp.persistent or insp.detached:
                        return

        # Iterate until the slug is unique.
        with session.no_autoflush:
            slug = unique(self, self.query, self.__class__.slug, unique_candidate)

        # Finally set the unique slug value.
        self.slug = slug
