"""Test for elements defined in init module."""

from mock import Mock

import pyramid_basemodel
from pyramid_basemodel import bind_engine, save


def test_save():
    """Test save method."""
    mock_session = Mock()
    save("a", session=mock_session)
    mock_session.add.assert_called_with("a")

    save(["a", "b"], session=mock_session)
    mock_session.add_all.assert_called_with(["a", "b"])


def test_bind_engine():
    """Test default bind engine behaviour."""
    mock_session = Mock()
    mock_base = Mock()
    mock_engine = Mock()

    bind_engine(mock_engine, session=mock_session, base=mock_base)
    mock_session.configure.assert_called_with(bind=mock_engine)

    assert mock_base.metadata.bind == mock_engine

    assert not mock_base.metadata.create_all.called
    assert not mock_base.metadata.drop_all.called


def test_bind_engine_create():
    """Test whether bind_engine triggers create_all if requested."""
    mock_base = Mock()
    bind_engine(Mock(), session=Mock(), base=mock_base, should_create=True)

    assert mock_base.metadata.create_all.called
    assert not mock_base.metadata.drop_all.called


def test_bind_engine_drop():
    """Test whether bind_engine triggers drop_all if requested."""
    mock_base = Mock()
    bind_engine(Mock(), session=Mock(), base=mock_base, should_drop=True)

    assert not mock_base.metadata.create_all.called
    assert mock_base.metadata.drop_all.called


def test_includeme(monkeypatch):
    """Default includeme behaviour."""
    mocked_engine_from_config = Mock()
    mocked_engine_from_config.return_value = "engine"

    monkeypatch.setattr(pyramid_basemodel, "engine_from_config", mocked_engine_from_config)
    monkeypatch.setattr(pyramid_basemodel, "bind_engine", Mock())

    mock_config = Mock()
    configure_mock = {"registry.settings": {}}
    mock_config.configure_mock(**configure_mock)
    mock_config.get_settings.return_value = mock_config.registry.settings
    pyramid_basemodel.includeme(mock_config)

    mock_config.action.assert_called_with(
        None, pyramid_basemodel.bind_engine, ("engine",), {"should_create": False, "should_drop": False}
    )


def test_includeme_nobind():
    """Test includeme should not bind behaviour."""
    mock_config = Mock()
    configure_mock = {"registry.settings": {"basemodel.should_bind_engine": False}}
    mock_config.configure_mock(**configure_mock)
    mock_config.get_settings.return_value = mock_config.registry.settings
    pyramid_basemodel.includeme(mock_config)
    assert not mock_config.action.called
