"""Slug test module."""

import pytest
from mock import MagicMock
from sqlalchemy import Column, Integer

from pyramid_basemodel import Base
from pyramid_basemodel.slug import BaseSlugNameMixin


@pytest.fixture
def sample_model():
    """Sample model fixture."""

    class Model(Base, BaseSlugNameMixin):
        __tablename__ = "models"
        id = Column(Integer, primary_key=True)

    inst = Model()
    inst.query = MagicMock()
    yield inst

    # Remove table from declarative base
    Base.metadata.remove(Model.__table__)
    Base.registry.dispose()


def test_set_slug_is_slug_no_name(sample_model):
    """Test that slug won't be generated if already present."""
    mock_unique = MagicMock()

    sample_model.name = None
    sample_model.slug = "slug"
    sample_model.set_slug(unique=mock_unique)
    assert not mock_unique.called
    assert sample_model.slug == "slug"


def test_set_slug_is_slug_is_name(sample_model):
    """Test that slug won't be generated if it's same as candidate."""
    mock_inspect = MagicMock()
    mock_unique = MagicMock()

    sample_model.slug = "abc"
    sample_model.name = "Abc"
    sample_model.set_slug(candidate="abc", inspect=mock_inspect, unique=mock_unique)
    assert not mock_unique.called
    assert mock_inspect.called is True
    assert sample_model.slug == "abc"


def test_set_slug_no_slug_no_name(sample_model):
    """Test that the slug will be a random digest if the name is not set."""
    sample_model.slug = None
    sample_model.name = None
    sample_model.set_slug(unique=lambda *args: args[-1])
    assert len(sample_model.slug) == 32


def test_set_slug_no_slug_is_name(sample_model):
    """Test correct slugification of a name."""
    sample_model.name = "My nice name"
    sample_model.set_slug(unique=lambda *args: args[-1])
    assert sample_model.slug == "my-nice-name"


def test_set_slug_slug_unique(sample_model):
    """Test that the unique function get's called."""
    sample_model.slug = None
    sample_model.name = "My nice name"
    sample_model.set_slug(unique=lambda *args: "{0}-1".format(args[-1]))
    assert sample_model.slug == "my-nice-name-1"


def test_set_slug_truncate(sample_model):
    """Test that the slug is truncated."""
    mock_unique = MagicMock()
    sample_model.name = "a" * 95
    sample_model.set_slug(unique=mock_unique)
    assert len(mock_unique.call_args[0][3]) == 61
