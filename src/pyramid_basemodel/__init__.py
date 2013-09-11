# -*- coding: utf-8 -*-

"""Provides global scoped ``Session`` and declarative ``Base``, ``BaseMixin``
  class and ``bind_engine`` function.
  
  To use, import and, e.g.: inherit from the base classes::
  
      >>> class MyModel(Base, BaseMixin):
      ...     __tablename__ = 'my_model'
      ... 
      >>> instance = MyModel()
      >>> Session.add(instance)
      >>> # etc.
  
  To automatically bind the base metadata and session to your db engine, just
  include the package::
  
      config.include('pyramid_basemodel')
  
"""

__all__ = [
    'Base',
    'BaseMixin',
    'Session',
    'bind_engine',
]

import sys

# Make inflect optional for python3.
try:
    import inflect
except ImportError:
    if sys.version_info[0] == 2:
        raise
    inflect = None

from datetime import datetime

from zope.interface import classImplements
from zope.sqlalchemy import ZopeTransactionExtension

from sqlalchemy import engine_from_config
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from pyramid.settings import asbool

from .interfaces import IDeclarativeBase

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
classImplements(Base, IDeclarativeBase)

class classproperty(object):
    """A basic [class property](http://stackoverflow.com/a/3203659)."""
    
    def __init__(self, getter):
        self.getter = getter
    
    def __get__(self, instance, owner):
        return self.getter(owner)
    


class BaseMixin(object):
    """Provides an int ``id`` as primary key, ``version``, ``created`` and
      ``modified`` columns and a scoped ``self.query`` property.
    """
    
    id =  Column(Integer, primary_key=True)
    
    version = Column('v', Integer, default=1)
    created = Column('c', DateTime, default=datetime.utcnow)
    modified = Column('m', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    query = Session.query_property()
    
    @classproperty
    def class_name(cls):
        """Either returns ``cls._class_name``, if provided, or defaults to
          the singular of ``cls.plural_class_name``, which is derived from
          the tablename::
          
              >>> class Foo(BaseMixin):
              ...     __tablename__ = 'flobbles'
              ... 
              >>> Foo.class_name
              'Flobble'
              >>> foo = Foo()
              >>> foo.class_name
              'Flobble'
              >>> Foo._class_name = 'Baz'
              >>> foo = Foo()
              >>> foo.class_name
              'Baz'
          
          If singularising the plural class name doesn't work, uses the
          ``cls.__name__``::
          
              >>> class Foo(BaseMixin):
              ...     plural_class_name = 'Not Plural'
              ... 
              >>> Foo.class_name
              'Foo'
          
        """
        
        # Try the manual override.
        if hasattr(cls, '_class_name'):
            return cls._class_name
        
        # Try the inflect lib.
        if inflect is not None:
            singularise = inflect.engine().singular_noun
            name = singularise(cls.plural_class_name)
            if name:
                return name
        
        # If that didn't work, fallback on the class name.
        return cls.__name__
    
    @classproperty
    def class_slug(cls):
        """Either returns ``cls._class_slug``, if provided, or defaults to
          the tablename::
          
              >>> class Foo(BaseMixin):
              ...     __tablename__ = 'foos'
              ... 
              >>> Foo.class_slug
              'foos'
              >>> foo = Foo()
              >>> foo.class_slug
              'foos'
              >>> Foo._class_slug = 'bazaramas'
              >>> foo = Foo()
              >>> foo.class_slug
              'bazaramas'
          
        """
        
        return getattr(cls, '_class_slug', cls.__tablename__)
    
    @classproperty
    def singular_class_slug(cls):
        """Either returns ``self._singular_class_slug``, if provided, or defaults
          to a singular version of ``cls.class_slug``. If that's not found, falls
          back on the lowercase last word of the class name::
          
              >>> class Material(BaseMixin):
              ...     __tablename__ = 'materials'
              ... 
              >>> Material.singular_class_slug
              'material'
              >>> m = Material()
              >>> m.singular_class_slug
              'material'
              >>> class ProcessMaterials(BaseMixin):
              ...     __tablename__ = 'process_materials'
              ... 
              >>> ProcessMaterials.singular_class_slug
              'process_material'
              >>> ProcessMaterials.class_slug = 'XXXXXX_NO_SINGULAR_XXXXX'
              >>> ProcessMaterials.singular_class_slug
              'material'
              >>> ProcessMaterials._singular_class_slug = 'material'
              >>> ProcessMaterials.singular_class_slug
              'materials'
              >>> 
          
        """
        
        # If provided, use ``self._singular_class_slug``.
        if hasattr(cls, '_singular_class_slug'):
            return cls._singular_class_slug
        
        # Otherwise singularise the class_slug.
        if inflect is not None:
            singularise = inflect.engine().singular_noun
            slug = singularise(cls.class_slug)
            if slug:
                return slug
        
        # If that didn't work, fallback on the class name.
        return cls.class_name.split()[-1].lower()
    
    @classproperty
    def plural_class_name(cls):
        """Either returns ``self._plural_class_name``, if provided, or defaults
          to a title cases version of the tablename, with underscores replaced
          with spaces::
          
              >>> class Material(BaseMixin):
              ...     __tablename__ = 'materials'
              ... 
              >>> Material.plural_class_name
              'Materials'
              >>> m = Material()
              >>> m.plural_class_name
              'Materials'
              >>> class ProcessMaterials(BaseMixin):
              ...     __tablename__ = 'process_materials'
              ... 
              >>> ProcessMaterials.plural_class_name
              'Process Materials'
              >>> ProcessMaterials._plural_class_name = 'Pro Materials'
              >>> ProcessMaterials.plural_class_name
              'Pro Materials'
          
        """
        
        # If provided, use ``self._plural_class_name``.
        if hasattr(cls, '_plural_class_name'):
            return cls._plural_class_name
        
        # Otherwise pluralise the literal class name.
        return cls.__tablename__.replace('_', ' ').title()
    


def save(instance_or_instances, session=Session):
    """Save model instance(s) to the db.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_session = Mock()
      
      A single instance is added to the session::
      
          >>> save('a', session=mock_session)
          >>> mock_session.add.assert_called_with('a')
      
      Multiple instances are all added at the same time::
      
          >>> save(['a', 'b'], session=mock_session)
          >>> mock_session.add_all.assert_called_with(['a', 'b'])
      
    """
    
    v = instance_or_instances
    if isinstance(v, list) or isinstance(v, tuple):
        session.add_all(v)
    else:
        session.add(v)

def bind_engine(engine, session=Session, base=Base, should_create=True,
        should_drop=False):
    """Bind the ``session`` and ``base`` to the ``engine``.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_session = Mock()
          >>> mock_base = Mock()
          >>> mock_engine = Mock()
      
      Binds the session::
      
          >>> bind_engine(mock_engine, session=mock_session, base=mock_base)
          >>> mock_session.configure.assert_called_with(bind=mock_engine)
      
      Binds the base metadata::
      
          >>> mock_base.metadata.bind == mock_engine
          True
      
      Creates tables if they don't exist::
      
          >>> mock_base.metadata.create_all.assert_called_with(mock_engine)
      
      Unless ``should_create`` is ``False``::
      
          >>> mock_base = Mock()
          >>> bind_engine(mock_engine, session=mock_session, base=mock_base,
          ...             should_create=False)
          >>> mock_base.metadata.create_all.called
          False
      
      Drops tables if ``should_drop`` is ``True``::
      
          >>> mock_base.metadata.drop_all.called
          False
          >>> bind_engine(mock_engine, session=mock_session, base=mock_base,
          ...             should_drop=True)
          >>> mock_base.metadata.drop_all.assert_called_with(mock_engine)
      
    """
    
    session.configure(bind=engine)
    base.metadata.bind = engine
    if should_drop:
        base.metadata.drop_all(engine)
    if should_create:
        base.metadata.create_all(engine)

def includeme(config):
    """Bind to the db engine specifed in ``config.registry.settings``.
      
      Setup::
      
          >>> from mock import Mock
          >>> import pyramid_basemodel
          >>> _engine_from_config = pyramid_basemodel.engine_from_config
          >>> _bind_engine = pyramid_basemodel.bind_engine
          >>> pyramid_basemodel.engine_from_config = Mock()
          >>> pyramid_basemodel.engine_from_config.return_value = 'engine'
          >>> pyramid_basemodel.bind_engine = Mock()
          >>> mock_config = Mock()
          >>> mock_config.registry.settings = {}
      
      Calls ``bind_engine`` with the configured ``engine``::
      
          >>> includeme(mock_config)
          >>> pyramid_basemodel.bind_engine.assert_called_with('engine', 
          ...         should_create=True, should_drop=False)
      
      Teardown::
      
          >>> pyramid_basemodel.engine_from_config = _engine_from_config
          >>> pyramid_basemodel.bind_engine = _bind_engine 
      
    """
    
    # Bind the engine.
    settings = config.registry.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    should_create = asbool(settings.get('basemodel.should_create_all', True))
    should_drop = asbool(settings.get('basemodel.should_drop_all', False))
    bind_engine(engine, should_create=should_create, should_drop=should_drop)

