from mock import MagicMock

from pyramid_basemodel.util import get_object_id


def test_get_object_id():
    "Check get object id utility function."
    mock_user = MagicMock()
    mock_user.__tablename__ = 'users'
    mock_user.id = 1234
    assert get_object_id(mock_user) == 'users#1234'
