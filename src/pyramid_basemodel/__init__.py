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

from datetime import datetime

from sqlalchemy import engine_from_config
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from pyramid.settings import asbool
from zope.sqlalchemy import ZopeTransactionExtension

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class BaseMixin(object):
    """Provides an int ``id`` as primary key, ``version``, ``created`` and
      ``modified`` columns and a scoped ``self.query`` property.
    """
    
    id =  Column(Integer, primary_key=True)
    
    version = Column('v', Integer, default=1)
    created = Column('c', DateTime, default=datetime.utcnow)
    modified = Column('m', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    query = Session.query_property()


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

