pyramid_basemodel
=================

**pyramid_basemodel** is a thin, low level package that provides an SQLAlchemy
declarative `Base` and a thread local scoped `Session` that can be used by
different packages whilst only needing to be bound to a db engine once.

Usage
-----

You can use these as base classes for declarative model definitions, e.g.:

.. code-block:: python

    from pyramid_basemodel import Base, BaseMixin, Session, save

    class MyModel(Base, BaseMixin):
        """Example model class."""

        @classmethod
        def do_foo(cls):
            instance = Session.query(cls).first()
            save(instance)


You can then bind these to the `sqlalchemy.url` in your paster `.ini` config by
importing your model and this package, e.g.:

.. code-block:: python

    # for example in yourapp.__init__.py
    import mymodel

    def main(global_config, **settings):
        config = Configurator(settings=settings)
        config.include('pyramid_basemodel')
        config.include('pyramid_tm')
        return config.make_wsgi_app()

To pass extra keyword arguments to SQLAlchemy's `engine_from_config`, point the
`sqlalchemy.engine_kwargs_factory` setting at a callable by its dotted name:

.. code-block:: ini

    [app:main]
    sqlalchemy.url = postgresql://localhost/mydb
    sqlalchemy.engine_kwargs_factory = yourapp.db:engine_kwargs

The callable receives the application registry and returns a dictionary of keyword
arguments, e.g.:

.. code-block:: python

    # for example in yourapp/db.py
    def engine_kwargs(registry):
        return {"connect_args": {"application_name": "yourapp"}}

Use it for arguments that a paster `.ini` value cannot express, such as objects or
nested dictionaries. If the `sqlalchemy.pool_class` setting is also given, it
overrides any `poolclass` the factory returns.

Or if this is all too much voodoo, you can just use the `bind_engine` function:

.. code-block:: python

    from pyramid_basemodel import bind_engine
    from mypackage import mymodel

    # assuming `engine` is a bound SQLAlchemy engine.
    bind_engine(engine)

Note that the `Session` is designed to be used in tandem with [pyramid_tm][].
If you don't include `pyramid_tm`, you'll need to take care of committing
transactions yourself.

Tests
-----

To run the tests use:

.. code-block::

    py.test -v --cov pyramid_basemodel tests/

[pyramid_basemodel]: http://github.com/fizyk/pyramid_basemodel
[pyramid_simpleauth]: http://github.com/thruflo/pyramid_simpleauth
[pyramid_tm]: http://pyramid_tm.readthedocs.org
