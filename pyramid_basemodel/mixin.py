# -*- coding: utf-8 -*-

"""Provides shared mixins for ORM classes."""

__all__ = [
    "PolymorphicBaseMixin",
    "PolymorphicMixin",
    "TouchMixin",
]

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import Unicode
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from pyramid_basemodel import save as save_to_db

logger = logging.getLogger(__name__)


class PolymorphicBaseMixin:
    """PolymorphicMixin streamline inheritance.

    Provides a dynamically generated ``__mapper_args__`` property for
    [single table inherited][] ORM classes::

    [single table inherited]: http://bit.ly/TBDmMx
    """

    discriminator: Mapped[str | None] = mapped_column("type", Unicode(16))

    @declared_attr.directive
    def __mapper_args__(self) -> dict[str, Any]:
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        return {"polymorphic_on": self.discriminator, "polymorphic_identity": self.__class__.__name__.lower()}


class PolymorphicMixin:
    """PolymorphicMixin streamline inheritance.

    Provides a dynamically generated ``__mapper_args__`` property for
    [single table inherited][] ORM classes::

    [single table inherited]: http://bit.ly/TBDmMx
    """

    @declared_attr.directive
    def __mapper_args__(self) -> dict[str, Any]:
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        return {"polymorphic_identity": self.__class__.__name__.lower()}


class TouchMixin:
    """Provides ``touch`` and ``propagate_touch`` methods."""

    #: Provided by ``BaseMixin`` when the two are combined on a model.
    modified: Mapped[datetime | None]

    def propagate_touch(self) -> None:
        """Override to propagate touch events to relations.

        Note that this event *should not* be  called in response to an
        SQLAlchemy ORM attribute modified event, as you can't reliably
        update relations in an attribute event handler.
        """

    def touch(
        self,
        *,
        propagate: bool = True,
        now: Callable[[], datetime] = datetime.utcnow,
        save: Callable[..., None] = save_to_db,
    ) -> None:
        """Update self.modified."""
        # Update self's modified date.
        self.modified = now()
        save(self)

        # Call propagate touch.
        if propagate:
            self.propagate_touch()
