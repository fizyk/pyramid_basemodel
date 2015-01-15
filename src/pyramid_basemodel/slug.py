# -*- coding: utf-8 -*-

"""Provides a base ORM mixin for models that need a name and a url slug."""

__all__ = [
    'BaseSlugNameMixin',
]

import logging
logger = logging.getLogger(__name__)

import slugify

from sqlalchemy import exc as sa_exc
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext import declarative 
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode

from .util import ensure_unique
from .util import generate_random_digest

from . import Session

class BaseSlugNameMixin(object):
    """ORM mixin class that provides ``slug`` and ``name`` properties, with a
      ``set_slug`` method to set the slug value from the name and a default
      name aware factory classmethod.
    """
    
    _max_slug_length = 64
    _slug_is_unique = True

    @property
    def __name__(self):
        return self.slug
    
    
    @declarative.declared_attr
    def slug(cls):
        """A url friendly slug, e.g.: `foo-bar`."""
        
        l = cls._max_slug_length
        is_unique = cls._slug_is_unique
        return Column(Unicode(l), nullable=False, unique=is_unique)

    @declarative.declared_attr
    def name(cls):
        """A human readable name, e.g.: `Foo Bar`."""
        
        l = cls._max_slug_length
        return Column(Unicode(l), nullable=False)

    def set_slug(self, candidate=None, **kwargs):
        """Generate and set a unique ``self.slug`` from ``self.name``.
          
          Setup::
          
              >>> from mock import MagicMock as Mock
              >>> mock_inspect = Mock()
              >>> mock_unique = Mock()
              >>> return_none = lambda: None
              >>> return_true = lambda: True
              >>> from sqlalchemy.types import Integer
              >>> from pyramid_basemodel import Base
              >>> class Model(Base, BaseSlugNameMixin):
              ...     __tablename__ = 'models'
              ...     id =  Column(Integer, primary_key=True)
              >>> inst = Model()
              >>> inst.query = Mock()
              
          If there's a slug and no name, it's a noop::
          
              >>> inst.name = None
              >>> inst.slug = 'slug'
              >>> inst.set_slug(unique=mock_unique)
              >>> mock_unique.called
              False
              >>> inst.slug
              'slug'
              
          If there is a slug and a name and the slug is the candidate, then it's a noop::
          
              >>> inst.slug = u'abc'
              >>> inst.name = u'Abc'
              >>> inst.set_slug(candidate=u'abc', inspect=mock_inspect,
              ...         unique=mock_unique)
              >>> mock_unique.called
              False
              >>> mock_inspect.called
              True
              >>> inst.slug
              u'abc'
              
          If there's no name, uses a random digest::
          
              >>> mock_unique = lambda *args: args[-1]
              >>> inst.slug = None
              >>> inst.name = None
              >>> inst.set_slug(unique=mock_unique)
              >>> len(inst.slug)
              32
          
          Otherwise slugifies the name::
          
              >>> inst.name = u'My nice name'
              >>> inst.set_slug(unique=mock_unique)
              >>> inst.slug
              u'my-nice-name'
          
          Appending n until the slug is unique::
          
              >>> mock_unique = lambda *args: u'{0}-1'.format(args[-1])
              >>> inst.slug = None
              >>> inst.set_slug(unique=mock_unique)
              >>> inst.slug
              u'my-nice-name-1'

          Truncates the slug::

              >>> mock_unique = Mock()
              >>> inst.name = u'a' * 95
              >>> inst.set_slug(unique=mock_unique)
              >>> len(mock_unique.call_args[0][3])
              61
        """
        
        # Compose.
        gen_digest = kwargs.get('gen_digest', generate_random_digest)
        inspect = kwargs.get('inspect', sa_inspect)
        session = kwargs.get('session', Session)
        to_slug = kwargs.get('to_slug', slugify.slugify)
        unique = kwargs.get('unique', ensure_unique)

        # Generate a candidate slug.
        if candidate is None:
            if self.name:
                candidate = to_slug(self.name)
            if not candidate:
                candidate = gen_digest(num_bytes=16)
        
        # Make sure it's not longer than 64 chars.
        l = self._max_slug_length 
        l_minus_ellipsis = l - 3
        candidate = candidate[:l]
        unique_candidate = candidate[:l_minus_ellipsis]

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
