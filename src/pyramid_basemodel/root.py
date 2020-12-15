# -*- coding: utf-8 -*-

"""
Base traversal root and a mixin class for objects in the Pyramid traversal hierarchy.

Provides a base traversal root and a mixin class for objects in the Pyramid traversal hierarchy.

http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html
"""

__all__ = [
    "BaseRoot",
]

import logging

from zope.interface import implementer
from zope.interface import alsoProvides

from pyramid.interfaces import ILocation

logger = logging.getLogger(__name__)


@implementer(ILocation)
class BaseRoot:
    """Base class for traversal factories."""

    __name__ = ""
    __parent__ = None

    def locatable(self, context, key, provides=alsoProvides):
        """Make a context object locatable and return it."""
        if not hasattr(context, "__name__"):
            context.__name__ = key
        context._located_parent = self
        context.request = self.request
        if not ILocation.providedBy(context):
            provides(context, ILocation)
        return context

    def __init__(self, request, key="", parent=None):
        """Initialize BaseRoot class."""
        self.__name__ = key
        self.__parent__ = parent
        self.request = request
