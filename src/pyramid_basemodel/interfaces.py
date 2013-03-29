# -*- coding: utf-8 -*-

"""Marker interfaces for models and containers."""

__all__ = [
    'IModel',
    'IModelContainer',
]

from zope.interface import Attribute
from zope.interface import Interface

class IModel(Interface):
    """Provided by models."""

class IModelContainer(Interface):
    """Provided by model containers."""

