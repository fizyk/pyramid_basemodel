# -*- coding: utf-8 -*-
"""
Main pyramid_basemodel module.

Provides global scoped ``Session`` and declarative ``Base``, ``BaseMixin``
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

__version__ = "0.6.0"

__all__ = [
    "Base",
    "BaseMixin",
    "Session",
    "bind_engine",
]

import inflect
from datetime import datetime

from zope.interface import classImplements
from zope.sqlalchemy import register

from sqlalchemy import engine_from_config
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from pyramid.path import DottedNameResolver
from pyramid.settings import asbool

from pyramid_basemodel.interfaces import IDeclarativeBase

Session = scoped_session(sessionmaker())
register(Session)
Base = declarative_base()
classImplements(Base, IDeclarativeBase)


class classproperty:
    """A basic [class property](http://stackoverflow.com/a/3203659)."""

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class BaseMixin:
    """
    Default Base Model Mixin.

    Provides an int ``id`` as primary key, ``version``, ``created`` and
    ``modified`` columns and a scoped ``self.query`` property.
    """

    #: primary key
    id = Column(Integer, primary_key=True)

    #: schema version
    version = Column("v", Integer, default=1)

    #: timestamp of object creation
    created = Column("c", DateTime, default=datetime.utcnow)

    #: timestamp of object's latest update
    modified = Column("m", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    query = Session.query_property()

    @classproperty
    def class_name(cls):
        """
        Determine class name based on the _class_name or the __tablename__.

        If provided, defaults to ``cls._class_name``, otherwise default to
        ``cls.plural_class_name``, which is derived from the cls.__tablename__.

        If singularising the plural class name doesn't work, uses the
          ``cls.__name__``
        """
        # Try the manual override.
        if hasattr(cls, "_class_name"):
            return cls._class_name

        singularise = inflect.engine().singular_noun
        name = singularise(cls.plural_class_name)
        if name:
            return name

        # If that didn't work, fallback on the class name.
        return cls.__name__

    @classproperty
    def class_slug(cls):
        """Class slug based on either _class_slug or __tablename__."""
        return getattr(cls, "_class_slug", cls.__tablename__)

    @classproperty
    def singular_class_slug(cls):
        """Return singular version of ``cls.class_slug``."""
        # If provided, use ``self._singular_class_slug``.
        if hasattr(cls, "_singular_class_slug"):
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
        """Return plurar version of a class name."""
        # If provided, use ``self._plural_class_name``.
        if hasattr(cls, "_plural_class_name"):
            return cls._plural_class_name

        # Otherwise pluralise the literal class name.
        return cls.__tablename__.replace("_", " ").title()


def save(instance_or_instances, session=Session):
    """
    Save model instance(s) to the db.

    Both single and multiple instances can be saved.
    """
    v = instance_or_instances
    if isinstance(v, list) or isinstance(v, tuple):
        session.add_all(v)
    else:
        session.add(v)


def bind_engine(engine, session=Session, base=Base, should_create=False, should_drop=False):
    """
    Bind the ``session`` and ``base`` to the ``engine``.

    :param should_create: Triggers create tables on all models
    :param should_drop: Triggers drop on all tables
    """
    session.configure(bind=engine)
    base.metadata.bind = engine
    if should_drop:
        base.metadata.drop_all(engine)
    if should_create:
        base.metadata.create_all(engine)


def includeme(config):
    """Bind to the db engine specifed in ``config.registry.settings``."""
    # Bind the engine.
    settings = config.get_settings()
    engine_kwargs_factory = settings.pop("sqlalchemy.engine_kwargs_factory", None)
    if engine_kwargs_factory:
        kwargs_factory = config.maybe_dotted(engine_kwargs_factory)
        engine_kwargs = kwargs_factory(config.registry)
    else:
        engine_kwargs = {}
    pool_class = settings.pop("sqlalchemy.pool_class", None)
    if pool_class:
        dotted_name = DottedNameResolver()
        engine_kwargs["poolclass"] = dotted_name.resolve(pool_class)
    should_bind = asbool(settings.get("basemodel.should_bind_engine", True))
    should_create = asbool(settings.get("basemodel.should_create_all", False))
    should_drop = asbool(settings.get("basemodel.should_drop_all", False))
    if should_bind:
        engine = engine_from_config(settings, "sqlalchemy.", **engine_kwargs)
        config.action(
            None,
            bind_engine,
            (engine,),
            {"should_create": should_create, "should_drop": should_drop},
        )
