# -*- coding: utf-8 -*-

"""Provides a base ORM mixin for models that need a name and a url slug."""

__all__ = [
    'BaseSlugNameMixin',
]

import logging
logger = logging.getLogger(__name__)

import slugify

from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode

from .util import ensure_unique
from .util import generate_random_digest

class BaseSlugNameMixin(object):
    """ORM mixin class that provides ``slug`` and ``name`` properties, with a
      ``set_slug`` method to set the slug value from the name and a default
      name aware factory classmethod.
    """
    
    @property
    def __name__(self):
        return self.slug
    
    
    # A url friendly slug, e.g.: `foo-bar`.
    slug = Column(Unicode(64), nullable=False, unique=True)
    
    # A human readable name, e.g.: `Foo Bar`.
    name = Column(Unicode(64), nullable=False)
    
    def set_slug(self, candidate=None, to_slug=None, gen_digest=None, unique=None):
        """Generate and set a unique ``self.slug`` from ``self.name``.
          
          Setup::
          
              >>> from mock import MagicMock as Mock
              >>> return_none = lambda: None
              >>> return_true = lambda: True
              >>> def mock_n_aware_filter_by(slug=None):
              ...     mock_query = Mock()
              ...     if slug.endswith(str(1)):
              ...         mock_query.all.return_value = []
              ...     else:
              ...         mock_query.all.return_value = [True]
              ...     return mock_query
              ... 
              >>> mixin = BaseSlugNameMixin()
              >>> mixin.query = Mock()
          
          If there's a slug and no name, it's a noop::
          
              >>> mixin.name = None
              >>> mixin.slug = 'slug'
              >>> mixin.set_slug()
              >>> mixin.slug
              'slug'
              >>> mixin.query.filter_by.called
              False
          
          If there is a slug and a name and the slug starts with the sluggified
          name, then it's a noop::
          
              >>> mixin.slug = 'abc-1'
              >>> mixin.name = u'Abc'
              >>> mixin.set_slug()
              >>> mixin.slug
              'abc-1'
              >>> mixin.query.filter_by.called
              False
          
          If there's no name, uses a random digest::
          
              >>> mixin.slug = None
              >>> mixin.name = None
              >>> mixin.query.filter_by.return_value.first = return_none
              >>> mixin.set_slug()
              >>> len(mixin.slug)
              32
          
          Otherwise slugifies the name::
          
              >>> mixin.name = u'My nice name'
              >>> mixin.set_slug()
              >>> mixin.slug
              u'my-nice-name'
          
          Appending n until the slug is unique::
          
              >>> mixin.slug = None
              >>> mixin.query.filter_by = mock_n_aware_filter_by
              >>> mixin.set_slug()
              >>> mixin.slug
              u'my-nice-name-1'
          
          If the slug is never unique, falls back on a random digest::
          
              >>> mixin.query.filter_by = Mock()
              >>> mixin.query.filter_by.return_value.all.return_value = [True]
              >>> mixin.slug = None
              >>> mixin.set_slug()
              >>> len(mixin.slug.split('my-nice-name-')[1])
              16
          
        """
        
        # Compose.
        if to_slug is None:
            to_slug = slugify.slugify
        if gen_digest is None:
            gen_digest = generate_random_digest
        if unique is None:
            unique = ensure_unique
        
        # Generate a candidate slug.
        if candidate is None:
            if self.name:
                candidate = to_slug(self.name)
            else:
                candidate = gen_digest(num_bytes=16)
        
        # If there's no name, only set the slug if its not already set.
        if self.slug and not self.name:
            return
        
        # If there is a name and the slug matches it, then don't try and
        # reset (i.e.: we only want to set a slug if the name has changed).
        if self.slug and self.name:
            if self.slug == candidate:
                return
        
        # Iterate until the slug is unique.
        slug = unique(self, self.query, self.__class__.slug, candidate)
        
        # Set the slug value.
        self.slug = slug
    

