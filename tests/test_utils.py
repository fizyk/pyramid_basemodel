"""Test utils module."""

import hashlib

from mock import MagicMock, Mock
from sqlalchemy import schema

from pyramid_basemodel.util import (
    generate_random_digest,
    get_all_matching,
    get_object_id,
    get_or_create,
    table_args_indexes,
)


def test_get_object_id():
    """Check get object id utility function."""
    mock_user = MagicMock()
    mock_user.__tablename__ = "users"
    mock_user.id = 1234
    assert get_object_id(mock_user) == "users#1234"


def test_generate_random_digest_default():
    """Check digest length with default arguments."""
    h = hashlib.sha224()
    digest = generate_random_digest()
    assert len(h.hexdigest()) == len(digest)


def test_generate_random_digest_longer():
    """Check digest lenght with explicit num_bytes different than default."""
    h = hashlib.sha512()
    digest = generate_random_digest(num_bytes=64)
    assert len(h.hexdigest()) == len(digest)


def test_get_or_create_existing():
    """Test get_or_create where instance already exists."""
    mock_cls = Mock()
    mock_cls.return_value = "new"
    kwargs = dict(foo="bar")

    # mock returning existing instance
    mock_cls.query.filter_by.return_value.first.return_value = "exist"
    assert get_or_create(mock_cls, **kwargs) == "exist"
    mock_cls.query.filter_by.assert_called_with(**kwargs)


def test_get_or_create_new():
    """Test get_or_create where instance does not exists."""
    mock_cls = Mock()
    mock_cls.return_value = "new"
    kwargs = dict(foo="bar")
    # query returns nothing, so new instance will be created.
    mock_cls.query.filter_by.return_value.first.return_value = None
    assert get_or_create(mock_cls, **kwargs) == "new"
    mock_cls.assert_called_with(**kwargs)


def test_get_all_matching():
    """Test return all matching instances."""
    mock_cls = Mock()
    mock_cls.query.filter.return_value.all.return_value = ["result"]

    assert get_all_matching(mock_cls, "a", [1, 2, 3]) == ["result"]
    mock_cls.a.in_.assert_called_with([1, 2, 3])
    mock_cls.query.filter.assert_called_with(mock_cls.a.in_.return_value)


def test_table_args_indexes():
    """Test table_args_indexes to build proper indexes."""
    a = table_args_indexes(
        "basket_items",
        [
            "basket_id",
            ("c", "created"),
        ],
    )
    b = (
        schema.Index(
            "basket_items_basket_id_idx",
            "basket_id",
        ),
        schema.Index(
            "basket_items_c_idx",
            "created",
        ),
    )
    assert str(a) == str(b)
