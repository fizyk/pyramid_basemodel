# -*- coding: utf-8 -*-

"""Provides shared mixins for ORM classes."""

__all__ = [
    'PolymorphicBaseMixin',
    'PolymorphicMixin',
    'TouchMixin',
]

import logging
logger = logging.getLogger(__name__)

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declared_attr

from pyramid_basemodel import save as save_to_db

class PolymorphicBaseMixin(object):
    """Provides a dynamically generated ``__mapper_args__`` property for
      [single table inherited][] ORM classes::
      
      [single table inherited]: http://bit.ly/TBDmMx
    """
    
    discriminator = Column(u'type', Unicode(16))
    
    @declared_attr
    def __mapper_args__(self):
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        
        return {
            'polymorphic_on': self.discriminator,
            'polymorphic_identity': self.__class__.__name__.lower()
        }
    

class PolymorphicMixin(object):
    """Provides a dynamically generated ``__mapper_args__`` property for
      [single table inherited][] ORM classes::
      
      [single table inherited]: http://bit.ly/TBDmMx
    """
    
    @declared_attr
    def __mapper_args__(self):
        """Set the ``polymorphic_identity`` value to the lower case class name."""
        
        return {'polymorphic_identity': self.__class__.__name__.lower()}
    


class TouchMixin(object):
    """Provides ``touch`` and ``propagate_touch`` methods."""
    
    def propagate_touch(self):
        """Override to propagate touch events to relations.
          
          Note that this event *should not* be  called in response to an
          SQLAlchemy ORM attribute modified event, as you can't reliably
          update relations in an attribute event handler.
        """
    
    def touch(self, propagate=True, now=None, save=None):
        """Update self.modified."""
        
        # Compose.
        if now is None:
            now = datetime.utcnow
        if save is None:
            save = save_to_db
        
        # Update self's modified date.
        self.modified = now()
        save(self)
        
        # Call propagate touch.
        if propagate:
            self.propagate_touch()
    

