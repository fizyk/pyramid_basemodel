"""Blob module tests."""

from pyramid_basemodel.blob import Blob


def test_update_from_url(requests_mock):
    """Check whether the update_from_url reads the data from url as expected."""
    a_blob = Blob()
    url = "http://test.com"
    data = "data"
    requests_mock.get(url, text=data)
    a_blob.update_from_url(url)
    assert a_blob.value == data.encode()


def test_get_as_named_tempfile():
    """Check whether the namedfile is created correctly."""
    a_blob = Blob(value=b"data")
    f = a_blob.get_as_named_tempfile()
    f.file.seek(0)
    assert f.file.read() == a_blob.value
