from pyramid_basemodel import BaseMixin


def test_model_classname():
    "Test model's class name."
    class Foo(BaseMixin):
        __tablename__ = 'flobbles'

    assert Foo.class_name == 'Flobble'
    foo = Foo()
    assert foo.class_name == 'Flobble'
    Foo._class_name = 'Baz'
    foo = Foo()
    assert foo.class_name == 'Baz'


def test_model_classname_singular():
    "Test model singularise class name."
    class Foo(BaseMixin):
        plural_class_name = 'Not Plural'
    assert Foo.class_name == 'Foo'
