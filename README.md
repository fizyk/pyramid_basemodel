[pyramid_basemodel][] is a thin, low level package that provides an SQLAlchemy
declarative `Base` and a thread local scoped `Session` that can be used by
different packages whilst only needing to be bound to a db engine once.

# Usage

You can use these as base classes for declarative model definitions, e.g.::

    from pyramid_basemodel import Base, BaseMixin, Session, save
    
    class MyModel(Base, BaseMixin):
        """Example model class."""
        
        @classmethod
        def do_foo(cls):
            instance = Session.query(cls).first()
            save(instance)
        
    
You can then bind these to the `sqlalchemy.url` in your paster `.ini` config by
importing your model and this package, e.g.:

    # for example in yourapp.__init__.py
    import mymodel
    
    def main(global_config, **settings):
        config = Configurator(settings=settings)
        config.include('pyramid_basemodel')
        config.include('pyramid_tm')
        return config.make_wsgi_app()

Or if this is all too much voodoo, you can just use the `bind_engine` function::

    from pyramid_basemodel import bind_engine
    from mypackage import mymodel
    
    # assuming `engine` is a bound SQLAlchemy engine.
    bind_engine(engine)

Note that the `Session` is designed to be used in tandem with [pyramid_tm][].
If you don't include `pyramid_tm`, you'll need to take care of committing
transactions yourself.

# Tests

To run the tests use, e.g.:

    nosetests --cover-package=pyramid_base_model --cover-tests --with-doctest --with-coverage pyramid_basemodel
    ....
    Name                             Stmts   Miss  Cover   Missing
    --------------------------------------------------------------
    src/pyramid_basemodel/__init__      32      0   100%   
    ----------------------------------------------------------------------
    Ran 4 tests in 0.031s
    
    OK

[pyramid_basemodel]: http://github.com/thruflo/pyramid_basemodel
[pyramid_simpleauth]: http://github.com/thruflo/pyramid_basemodel
[pyramid_tm]: http://pyramid_tm.readthedocs.org
