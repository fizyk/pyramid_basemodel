"""Mixin test module."""

from mock import Mock, patch

from pyramid_basemodel.mixin import TouchMixin


def test_touch_mixin():
    """Check wether every argument of TouchMixin get's called in proper order."""
    t = TouchMixin()
    saved_arg = []

    def save_mock(instance):
        saved_arg.append(instance)

    assert not hasattr(t, "modified")
    with patch.object(t, "propagate_touch") as propagate_mock:
        t.touch(now=Mock, save=save_mock)
        assert propagate_mock.called
    assert hasattr(t, "modified")
    assert t == saved_arg[0]


def test_touch_mixin_no_propagate():
    """Check wether every argument of TouchMixin get's called in proper order."""
    t = TouchMixin()
    saved_arg = []

    def save_mock(instance):
        saved_arg.append(instance)

    assert not hasattr(t, "modified")
    with patch.object(t, "propagate_touch") as propagate_mock:
        t.touch(False, now=Mock, save=save_mock)
        assert not propagate_mock.called
    assert hasattr(t, "modified")
    assert t == saved_arg[0]
