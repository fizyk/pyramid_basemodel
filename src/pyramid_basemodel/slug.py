# -*- coding: utf-8 -*-

"""Provides a base ORM mixin for models that need a name and a url slug."""

__all__ = [
    "BaseSlugNameMixin",
]

import logging
import sys

if sys.version_info[0] == 3 and sys.version_info[1] <= 7:
    from typing_extensions import Protocol
else:
    from typing import Protocol

from slugify import slugify

from sqlalchemy import exc as sa_exc
from sqlalchemy import inspect
from sqlalchemy.ext import declarative
from sqlalchemy.orm import scoped_session, Query
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode

from pyramid_basemodel.util import ensure_unique, GenRandDigestProtocol
from pyramid_basemodel.util import generate_random_digest

from pyramid_basemodel import Session, Base

logger = logging.getLogger(__name__)


class UniqueFuncT(Protocol):
    """Unique function protocol."""

    def __call__(self, self_: Base, query: Query, property_: Column, value: str) -> str:
        ...


class BaseSlugNameMixin:
    """
    Base mixin delivering a slug functionality.

    ORM mixin class that provides ``slug`` and ``name`` properties, with a
    ``set_slug`` method to set the slug value from the name and a default
    name aware factory classmethod.
    """

    query: Query
    _max_slug_length: int = 64
    _slug_is_unique: bool = True

    @property
    def __name__(self) -> str:
        """Url friendly name."""
        return self.slug

    @declarative.declared_attr
    def slug(cls) -> Column:
        """Get url friendly slug, e.g.: `foo-bar`."""
        return Column(Unicode(cls._max_slug_length), nullable=False, unique=cls._slug_is_unique)

    @declarative.declared_attr
    def name(cls) -> Column:
        """Get human readable name, e.g.: `Foo Bar`."""
        return Column(Unicode(cls._max_slug_length), nullable=False)

    def set_slug(
        self,
        candidate: str = None,
        gen_digest: GenRandDigestProtocol = generate_random_digest,
        session: scoped_session = Session,
        unique: UniqueFuncT = ensure_unique,
    ) -> None:
        """
        Generate and set a unique ``self.slug`` from ``self.name``.

        :param get_digest: function to generate random digest. Used of there's no name set.
        :param to_slug: slugify function
        :param unique: unique function
        """
        # Generate a candidate slug.
        if candidate is None:
            if self.name:
                candidate = slugify(self.name)
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
