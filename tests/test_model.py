"""Model test module."""

from pyramid_basemodel import BaseMixin


def test_model_classname():
    """Test model's class name."""

    class Foo(BaseMixin):
        __tablename__ = "flobbles"

    assert Foo.class_name == "Flobble"
    foo = Foo()
    assert foo.class_name == "Flobble"
    Foo._class_name = "Baz"
    foo = Foo()
    assert foo.class_name == "Baz"


def test_model_classname_singular():
    """Test model singularise class name."""

    class Foo(BaseMixin):
        plural_class_name = "Not Plural"

    assert Foo.class_name == "Foo"


def test_model_class_slug():
    """Test model's class slug."""

    class Foo(BaseMixin):
        __tablename__ = "foos"

    assert not hasattr(Foo, "_class_slug")
    assert Foo.class_slug == Foo.__tablename__
    foo = Foo()
    assert foo.class_slug == Foo.__tablename__
    Foo._class_slug = "bazaramas"
    foo = Foo()
    foo.class_slug == "bazaramas"


def test_model_singular_class_slug():
    """Test model singular class slug."""

    class Material(BaseMixin):
        __tablename__ = "materials"

    assert Material.singular_class_slug == "material"
    m = Material()
    assert m.singular_class_slug == "material"

    class ProcessMaterials(BaseMixin):
        __tablename__ = "process_materials"

    assert ProcessMaterials.singular_class_slug == "process_material"
    ProcessMaterials.class_slug = "XXXXXX_NO_SINGULAR_XXXXX"
    assert ProcessMaterials.singular_class_slug == "material"
    ProcessMaterials._singular_class_slug = "materials"
    assert ProcessMaterials.singular_class_slug == "materials"


def test_model_plurar_class_name():
    """Test model plurar class name."""

    class Material(BaseMixin):
        __tablename__ = "materials"

    assert Material.plural_class_name == "Materials"
    m = Material()
    assert m.plural_class_name == "Materials"

    class ProcessMaterials(BaseMixin):
        __tablename__ = "process_materials"

    assert ProcessMaterials.plural_class_name == "Process Materials"
    ProcessMaterials._plural_class_name = "Pro Materials"
    assert ProcessMaterials.plural_class_name == "Pro Materials"
