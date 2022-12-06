CHANGES
=======

.. towncrier release notes start

0.5.3 (2022-12-06)
==================

Miscellaneus
------------

- Migrate automerge `fizyk/actions-reuse/.github/workflows/automerge-shared.yml`
  using github application for maintaining short lived acess tokens for merge-me actions. (`#297 <https://https://github.com/fizyk/pyramid_basemodel/issues/297>`_)
- Move as much of the project configuration to pyproject.toml as possible. And drop setup.py. (`#301 <https://https://github.com/fizyk/pyramid_basemodel/issues/301>`_)


0.5.2 (2022-11-25)
==================

Miscellaneus
------------

- Moved development dependency management into pipfile/pipfile.lock (`#283 <https://https://github.com/fizyk/pyramid_basemodel/issues/283>`_)
- Change versionin bumping tool from bumpversion to tbump (`#285 <https://https://github.com/fizyk/pyramid_basemodel/issues/285>`_)
- Updated package description to support python 3.11 (`#286 <https://https://github.com/fizyk/pyramid_basemodel/issues/286>`_)
- Added project urls to setup.cfg for better pypi.org experience. (`#287 <https://https://github.com/fizyk/pyramid_basemodel/issues/287>`_)


0.5.1
-----

* [package] Marked python 3.10 compatible (Trove Classifiers)

0.5.0
-----

* [simplify] Removed `inspect` and `to_slug` from `BaseSlugNameMixin.set_slug` method. These parameters seemd like a way 
  to override some core functionality, which seems like a rare enough case to not maintain it, especially without tests.
* [simplify] Removed `named_tempfile_cls` from `Blob.get_as_named_tempfile` as it wasn't used.
* [simplify] Simplified the `Blob.update_from_url`. Now the method accepts only url parameter and does exactly one thing.
* [code] Use default arguments instead of compose sections.

0.4.0
-----

* [enhancement] Switch slugify to python-slugify as the latter is python3 compatible
* [enhancement] As far as existing tests are concerned, now there's both full
  compatibility and feature parity between python 2 and python 3
* [CI] use CI

0.3.7
-----

* Fix support for zope.sqlalchemy >= 1.2

0.3.4
-----

* Remove stray print statements.

0.3.3
-----

* Bump to remove `src/*.egg-info` directory from PyPI distribution.

0.3.2
-----

* Make engine kwargs configurable.

0.3.1
-----

* Introduce the `basemodel.should_bind_engine` config flag, which can be used,
  e.g.: in ftests, to disable the automatic engine setup, even when application
  code `config.include('pyramid_basemodel')`\s.

  Defaults to `True`!

0.3
---

Default `basemodel.should_create_all` to `False`. This will break apps that rely on tables being created by default. However, it's much saner to only
invoke both `metadata.create_all(engine)` and `metadata.drop_all(engine)` when
explicitly told to, particularly as most applications will use migrations
to manage the database schema.

0.2.4 -> 0.2.6
--------------

Faff about horribly with the slug generation code.

0.2.3
-----

Fix Python3 `KeyError` syntax bug.

0.2.2
-----

Support dotted path `sqlalchemy.pool_class` configuration.

0.2.1
-----

Provide `util.get_object_id` function and stamp
`sqlalchemy.ext.declarative.declarative_base()` subclasses with the
`interfaces.IDeclarativeBase` interface.

0.2
---

Fix Python3 support (requires 3.3 for the unicode literal character).

0.1.8
-----

Allow concrete subclasses of ``BaseModelContainer`` to be provided in the
``tree.BaseContentRoot.mapping`` (as well as interfaces).

0.1.7
-----

Added a `pyramid_basemodel.blob.Blob` model class to store large binary files.

Fixed up `.slug` module doctests. Fix `install_requires` list in `setup.py`.

0.1.6
-----

Base the ``BaseMixin.class_name`` on a singularised version of the plural
class name.  This may seem a bit arse about face, but allows us to use the
tablename to split the word, e.g.:

.. code-block::

    >>> class OperatingScale(Base, BaseMixin):
    ...     __tablename__ 'operating_scales'
    ... 

    >>> OperatingScale.class_name
    'Operating Scale'

Just ignore all this if you don't plan on using the `class_name`, `class_slug` and
`plural_class_name` properties.

0.1.5
-----

Provide `BaseMixin.class_slug` and base it and the `BaseMixin.plural_class_name`
on the `cls.__tablename__` instead of the `cls.__name__`.

All still manually overrideable by providing the corresponding property with a
single underscore, e.g.: `cls._plural_class_name`.

0.1.4
-----

Provide `BaseMixin.class_name` and `BaseMixin.plural_class_name`.

0.1.3
-----

Bugfix to parse config options properly.

0.1.2
-----

Added `basemodel.should_create_all` configuration option.

