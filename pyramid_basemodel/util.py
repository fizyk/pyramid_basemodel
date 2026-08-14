# -*- coding: utf-8 -*-

"""Shared utility functions for interacting with the data model."""

import logging
import os
from binascii import hexlify
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Union

from sqlalchemy import schema
from sqlalchemy.orm import Query

logger = logging.getLogger(__name__)


def generate_random_digest(
    num_bytes: int = 28,
    urandom: Callable[[int], bytes] = os.urandom,
    to_hex: Callable[[bytes], bytes] = hexlify,
) -> str:
    """Generate a random hash and returns the hex digest as a unicode string.

    :param num_bytes: number of bytes to random(select)
    :param urandom: urandom function
    :param to_hex: hexifying function
    """
    # Get random bytes.
    r = urandom(num_bytes)

    # Return as a unicode string.
    return to_hex(r).decode("utf-8")


def ensure_unique(
    self: Any,
    query: Query[Any],
    property_: Any,
    value: str,
    max_iter: int = 30,
    gen_digest: Callable[..., str] = generate_random_digest,
) -> str:
    """Make sure slug is unique.

    Takes a ``candidate`` value for a unique ``property_`` and iterates,
    appending an incremented integer until unique.
    """
    # Unpack
    candidate = value

    # Iterate until the slug is unique.
    n = 0
    n_str = ""
    while True:
        # Keep trying slug, slug-1, slug-2, etc.
        value = f"{candidate}{n_str}"
        existing = None
        existing_instances = query.filter(property_ == value).all()
        for instance in existing_instances:
            if instance != self:
                existing = instance
                break
        if existing and n < 30:
            n += 1
            # If we've tried 1, 2 ... all the way to ``max_iter``, then
            # fallback on appending a random digest rather than a sequential
            # number.
            suffix = str(n) if n < 20 else gen_digest(num_bytes=8)
            n_str = f"-{suffix}"
            continue
        break

    return value


def get_or_create(cls: Any, **kwargs: Any) -> Any:
    """Get or create a ``cls`` instance using the ``kwargs`` provided."""
    instance = cls.query.filter_by(**kwargs).first()
    if not instance:
        instance = cls(**kwargs)
    return instance


def get_all_matching(cls: Any, column_name: str, values: Iterable[Any]) -> list[Any]:
    """Return all instances of ``cls`` where ``column_name`` matches one of ``values``.

    :param cls:
    :param column_name:
    :param values:
    """
    column = getattr(cls, column_name)
    query: Query[Any] = cls.query.filter(column.in_(values))
    return query.all()


def get_object_id(instance: Any) -> str:
    """Return an identifier that's unique across database tables."""
    return f"{instance.__tablename__}#{instance.id}"


def table_args_indexes(
    tablename: str,
    columns: Iterable[Union[str, Sequence[str]]],
) -> tuple[schema.Index, ...]:
    """Build table indexes.

    Call with a class name and a list of relation id columns to return the
    appropriate op.execute created indexes.

    This is useful as a way to tell `alembic revision --autogenerate` that
    these indexes should exist, even when created manually using `op.execute`.

    Ref: https://bitbucket.org/zzzeek/alembic/issues/233/add-indexes-to-include_object-hook
    """
    indexes: list[schema.Index] = []
    for item in columns:
        # NOTE: the length check, not the item type, decides how an entry is
        # unpacked. Kept as-is to preserve behaviour.
        db_name: Any
        attr_name: Any
        if len(item) == 2:
            db_name = item[0]  # db column
            attr_name = item[1]  # sqlalchemy attr
        else:
            db_name = item
            attr_name = item
        idx_name = f"{tablename}_{db_name}_idx"
        idx = schema.Index(idx_name, attr_name)
        indexes.append(idx)
    return tuple(indexes)
