# -*- coding: utf-8 -*-

"""Shared utility functions for interacting with the data model."""

import logging
logger = logging.getLogger(__name__)

import os
from binascii import hexlify

from sqlalchemy import schema

def generate_random_digest(num_bytes=28, urandom=None, to_hex=None):
    """
    Generates a random hash and returns the hex digest as a unicode string.

    :param num_bytes: number of bytes to random(select)
    :param urandom: urandom function
    :param to_hex: hexifying function
    """
    
    # Compose.
    if urandom is None:
        urandom = os.urandom
    if to_hex is None:
        to_hex = hexlify
    
    # Get random bytes.
    r = urandom(num_bytes)
    
    # Return as a unicode string.
    return to_hex(r).decode("utf-8")

def ensure_unique(self, query, property_, value, max_iter=30, gen_digest=None):
    """Takes a ``candidate`` value for a unique ``property_`` and iterates,
      appending an incremented integer until unique.
    """
    
    # Compose.
    if gen_digest is None:
        gen_digest = generate_random_digest
    
    # Unpack
    candidate = value
    
    # Iterate until the slug is unique.
    n = 0
    n_str = ''
    while True:
        # Keep trying slug, slug-1, slug-2, etc.
        value = u'{0}{1}'.format(candidate, n_str)
        existing = None
        existing_instances = query.filter(property_==value).all()
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
            n_str = u'-{0}'.format(suffix)
            continue
        break
    
    return value

def get_or_create(cls, **kwargs):
    "Get or create a ``cls`` instance using the ``kwargs`` provided."
    
    instance = cls.query.filter_by(**kwargs).first()
    if not instance:
        instance = cls(**kwargs)
    return instance

def get_all_matching(cls, column_name, values):
    """
    Return all instances of ``cls`` where ``column_name`` matches one of ``values``.

    :param cls:
    :param column_name:
    :param values:
    """

    column = getattr(cls, column_name)
    query = cls.query.filter(column.in_(values))
    return query.all()


def get_object_id(instance):
    "Return an identifier that's unique across database tables."
    return u'{0}#{1}'.format(instance.__tablename__, instance.id)


def table_args_indexes(tablename, columns):
    """Call with a class name and a list of relation id columns to return the
      appropriate op.execute created indexes.

      This is useful as a way to tell `alembic revision --autogenerate` that
      these indexes should exist, even when created manually using `op.execute`.

      Ref: https://bitbucket.org/zzzeek/alembic/issues/233/add-indexes-to-include_object-hook
    """

    indexes = []
    for item in columns:
        if len(item) == 2:
            db_name = item[0] # db column
            attr_name = item[1] # sqlalchemy attr
        else:
            db_name = item
            attr_name = item
        idx_name = '{0}_{1}_idx'.format(tablename, db_name)
        idx = schema.Index(idx_name, attr_name)
        indexes.append(idx)
    return tuple(indexes)
