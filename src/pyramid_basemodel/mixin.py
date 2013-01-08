# -*- coding: utf-8 -*-

"""Provides shared mixins for ORM classes."""

__all__ = [
    'PolymorphicBaseMixin',
    'PolymorphicMixin'
]

import logging
logger = logging.getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declared_attr

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
    

