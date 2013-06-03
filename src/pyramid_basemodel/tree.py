# -*- coding: utf-8 -*-

"""Provide a ``BaseContentRoot`` traversal root for looking up instances
  via their containers.
"""

__all__ = [
    'BaseContentRoot',
]

import logging
logger = logging.getLogger(__name__)

from zope.interface import Interface
from zope.interface import alsoProvides

from .container import BaseModelContainer
from .root import BaseRoot

class BaseContentRoot(BaseRoot):
    """Base logic for looking up models."""
    
    apex = None # e.g.: (Design, IDesignsContainer, {})
    mapping = {} # {u'formats': (FileFormat, IFileFormatsContainer, {}), ...}
    
    def container_factory(self, item, key, provides=None, default_cls=None,
            interface_cls=None):
        """Return an instantiated and interface providing container."""
        
        # Compose.
        if provides is None:
            provides = alsoProvides
        if default_cls is None:
            default_cls = BaseModelContainer
        if interface_cls is None:
            interface_cls = Interface
        
        # Unpack the mapping item.
        model_cls, container_cls_or_interface, kwargs = item
        
        # If the container_cls_or_interface is an interface, then use the
        # default container cls and mark the instance as providing it.
        is_interface = issubclass(container_cls_or_interface, interface_cls)
        if is_interface:
            container_cls = default_cls
            container_interface = container_cls_or_interface
        else:
            container_cls = container_cls_or_interface
        
        # Instantiate the model container.
        container = container_cls(self.request, model_cls, key=key,
                parent=self, **kwargs)
        
        # Patch it to provide the specific container interface.
        if is_interface:
            provides(container, container_cls_or_interface)
        
        # Return the container.
        return container
    
    def __getitem__(self, key):
        """First see if the key is in ``self.mapping``. If it is, return
          a content container configured to look up that model class.
        """
        
        # If the key matches a traversal container in the mapping, use that.
        if key in self.mapping:
            mapping_item = self.mapping.get(key)
            return self.container_factory(mapping_item, key)
        
        # Otherwise try and lookup using the apex model class.
        if self.apex:
            container = self.container_factory(self.apex, '')
            return self.locatable(container[key], key)
        
        raise KeyError(key)
    

