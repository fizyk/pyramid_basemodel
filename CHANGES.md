
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

