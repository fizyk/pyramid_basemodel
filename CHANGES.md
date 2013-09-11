
# 0.2.1

Provide `util.get_object_id` function and stamp
`sqlalchemy.ext.declarative.declarative_base()` subclasses with the
`interfaces.IDeclarativeBase` interface.

# 0.2

Fix Python3 support (requires 3.3 for the unicode literal character).

# 0.1.8

Allow concrete subclasses of ``BaseModelContainer`` to be provided in the
``tree.BaseContentRoot.mapping`` (as well as interfaces).

# 0.1.7

Added a `pyramid_basemodel.blob.Blob` model class to store large binary files.

Fixed up `.slug` module doctests. Fix ``install_requires` list in `setup.py`.

# 0.1.6

Base the ``BaseMixin.class_name`` on a singularised version of the plural
class name.  This may seem a bit arse about face, but allows us to use the
tablename to split the word, e.g.:

    >>> class OperatingScale(Base, BaseMixin):
    ...     __tablename__ 'operating_scales'
    ... 
    >>> OperatingScale.class_name
    'Operating Scale'

Just ignore all this if you don't plan on using the `class_name`, `class_slug` and
`plural_class_name` properties.

# 0.1.5

Provide `BaseMixin.class_slug` and base it and the `BaseMixin.plural_class_name`
on the `cls.__tablename__` instead of the `cls.__name__`.

All still manually overrideable by providing the corresponding property with a
single underscore, e.g.: `cls._plural_class_name`.

# 0.1.4

Provide `BaseMixin.class_name` and `BaseMixin.plural_class_name`.

# 0.1.3

Bugfix to parse config options properly.

# 0.1.2

Added `basemodel.should_create_all` configuration option.

