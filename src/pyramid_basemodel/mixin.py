# -*- coding: utf-8 -*-

"""Provides shared mixins for ORM classes."""

__all__ = [
    "PolymorphicBaseMixin",
    "PolymorphicMixin",
    "TouchMixin",
]

import logging

from datetime import datetime
from typing import Callable, Protocol, List, Union, Tuple

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta

from pyramid_basemodel import save as save_to_db

logger = logging.getLogger(__name__)


class PolymorphicBaseMixin:
    """
    PolymorphicMixin streamline inheritance.

    Provides a dynamically generated ``__mapper_args__`` property for
    [single table inherited][] ORM classes::

    [single table inherited]: http://bit.ly/TBDmMx
    """

    discriminator = Column("type", Unicode(16))

    @declared_attr
    def __mapper_args__(self: "PolymorphicBaseMixin") -> dict:
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        return {"polymorphic_on": self.discriminator, "polymorphic_identity": self.__class__.__name__.lower()}


class PolymorphicMixin:
    """
    PolymorphicMixin streamline inheritance.

    Provides a dynamically generated ``__mapper_args__`` property for
    [single table inherited][] ORM classes::

    [single table inherited]: http://bit.ly/TBDmMx
    """

    @declared_attr
    def __mapper_args__(self) -> dict:
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        return {"polymorphic_identity": self.__class__.__name__.lower()}


class TouchMixin:
    """Provides ``touch`` and ``propagate_touch`` methods."""

    def propagate_touch(self) -> None:
        """
        Override to propagate touch events to relations.

        Note that this event *should not* be  called in response to an
        SQLAlchemy ORM attribute modified event, as you can't reliably
        update relations in an attribute event handler.
        """

    def touch(
        self,
        propagate: bool = True,
        now: Callable[[], datetime] = datetime.utcnow,
        save: Callable[[Union[List[DeclarativeMeta], Tuple[DeclarativeMeta, ...], DeclarativeMeta]], None] = save_to_db,
    ) -> None:
        """Update self.modified."""
        # Update self's modified date.
        self.modified = now()
        save(self)

        # Call propagate touch.
        if propagate:
            self.propagate_touch()
