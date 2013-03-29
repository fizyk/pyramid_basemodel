# -*- coding: utf-8 -*-

"""Provides a base traversal root and a mixin class for objects in the
  Pyramid traversal hierarchy.
  
  http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html
"""

__all__ = [
    'BaseRoot',
]

import logging
logger = logging.getLogger(__name__)

from zope.interface import implementer
from zope.interface import alsoProvides

from pyramid.interfaces import ILocation

@implementer(ILocation)
class BaseRoot(object):
    """Base class for traversal factories."""
    
    __name__ = ''
    __parent__ = None
    
    def locatable(self, context, key, provides=None):
        """Make a context object locatable and return it."""
        
        # Compose.
        if provides is None:
            provides = alsoProvides
        
        if not hasattr(context, '__name__'):
            context.__name__ = key
        context._located_parent = self
        context.request = self.request
        if not ILocation.providedBy(context):
            provides(context, ILocation)
        return context
    
    def __init__(self, request, key='', parent=None):
        self.__name__ = key
        self.__parent__ = parent
        self.request = request
    

