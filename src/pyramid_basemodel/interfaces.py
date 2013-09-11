# -*- coding: utf-8 -*-

"""Marker interfaces for models and containers."""

__all__ = [
    'IDeclarativeBase',
    'IModel',
    'IModelContainer',
]

from zope.interface import Attribute
from zope.interface import Interface

class IDeclarativeBase(Interface):
    """Implemented by the declarative base and all classes that inherit from it."""

class IModel(IDeclarativeBase):
    """Provided by models."""

class IModelContainer(Interface):
    """Provided by model containers."""

