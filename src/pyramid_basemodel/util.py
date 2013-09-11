# -*- coding: utf-8 -*-

"""Shared utility functions for interacting with the data model."""

import logging
logger = logging.getLogger(__name__)

import os
from binascii import hexlify

def generate_random_digest(num_bytes=28, urandom=None, to_hex=None):
    """Generates a random hash and returns the hex digest as a unicode string.
      
      Defaults to sha224::
      
          >>> import hashlib
          >>> h = hashlib.sha224()
          >>> digest = generate_random_digest()
          >>> len(h.hexdigest()) == len(digest)
          True
      
      Pass in ``num_bytes`` to specify a different length hash::
      
          >>> h = hashlib.sha512()
          >>> digest = generate_random_digest(num_bytes=64)
          >>> len(h.hexdigest()) == len(digest)
          True
      
      Returns unicode::
      
          >>> type(digest) == type(u'')
          True
      
    """
    
    # Compose.
    if urandom is None:
        urandom = os.urandom
    if to_hex is None:
        to_hex = hexlify
    
    # Get random bytes.
    r = urandom(num_bytes)
    
    # Return as a unicode string.
    return unicode(to_hex(r))

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
    """Get or create a ``cls`` instance using the ``kwargs`` provided.
      
          >>> from mock import Mock
          >>> mock_cls = Mock()
          >>> kwargs = dict(foo='bar')
      
      If an instance matches the filter kwargs, return it::
      
          >>> mock_cls.query.filter_by.return_value.first.return_value = 'exist'
          >>> get_or_create(mock_cls, **kwargs)
          'exist'
          >>> mock_cls.query.filter_by.assert_called_with(**kwargs)
      
      Otherwise return a new instance, initialised with the ``kwargs``::
      
          >>> mock_cls = Mock()
          >>> mock_cls.return_value = 'new'
          >>> mock_cls.query.filter_by.return_value.first.return_value = None
          >>> get_or_create(mock_cls, **kwargs)
          'new'
          >>> mock_cls.assert_called_with(**kwargs)
      
    """
    
    instance = cls.query.filter_by(**kwargs).first()
    if not instance:
        instance = cls(**kwargs)
    return instance

def get_all_matching(cls, column_name, values):
    """Get all the instances of ``cls`` where the column called ``column_name``
      matches one of the ``values`` provided.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_cls = Mock()
          >>> mock_cls.query.filter.return_value.all.return_value = ['result']
      
      Queries and returns the results::
      
          >>> get_all_matching(mock_cls, 'a', [1,2,3])
          ['result']
          >>> mock_cls.a.in_.assert_called_with([1,2,3])
          >>> mock_cls.query.filter.assert_called_with(mock_cls.a.in_.return_value)
      
    """
    
    column = getattr(cls, column_name)
    query = cls.query.filter(column.in_(values))
    return query.all()

def get_object_id(instance):
    """Return an identifier that's unique across database tables, e.g.::
      
          >>> from mock import MagicMock
          >>> mock_user = MagicMock()
          >>> mock_user.__tablename__ = 'users'
          >>> mock_user.id = 1234
          >>> get_object_id(mock_user)
          u'users#1234'
      
    """
    
    return u'{0}#{1}'.format(instance.__tablename__, instance.id)

