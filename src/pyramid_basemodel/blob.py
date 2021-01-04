# -*- coding: utf-8 -*-

"""
Provide a generic model class for storing large binary objects.

To store a bytestring::

  blob = Blob.factory('foo') # sets the blob's name to 'foo'
  blob.value = b'baz'

To store a file::

  f = open('/tmp/foo.pdf')
  blob = Blob.factory('foo', file_like_object=f)
  save(blob)

To store a download from a url::

  blob = Blob.factory('foo')
  blob.update_from_url('http://www.example.com/foo.pdf')
  save(blob)

The Blob's ``value`` is a read only buffer, e.g. to iterate over the contents::

  while True:
      chunk = blob.value.read(1024)
      if chunk is None:
          break
      # do something with ``chunk``

"""

__all__ = [
    "Blob",
]

import logging
from http import HTTPStatus
from io import StringIO

from gzip import GzipFile
from tempfile import NamedTemporaryFile

import requests

from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode
from sqlalchemy.types import LargeBinary

from pyramid_basemodel import Base
from pyramid_basemodel import BaseMixin

logger = logging.getLogger(__name__)


class Blob(Base, BaseMixin):
    """
    Encapsulates a large binary file.

    Instances must have a unique ``self.name``, which has a maximum length
    of 64 characters.

    The binary data is stored in ``self.value``, either directly by assigning
    a bytestring, or passing a file like object to ``self.update()`` or by
    downloading a file from a url using ``self.update_from_url()``. The
    downloaded file can optionally be unzipped if compressed using gzip.

    When reading the data, ``self.value`` is a read only buffer. A convienience
    ``self.get_as_named_tempfile()`` method is provided as an easy way to get
    the value as a readable and writable file that can optionally be closed
    so the data is available from the filesystem.
    """

    __tablename__ = "blobs"

    name = Column(Unicode(64), nullable=False, unique=True)
    value = Column(LargeBinary, nullable=False)

    @classmethod
    def factory(cls, name, file_like_object=None):
        """Create and return."""
        instance = cls()
        instance.update(name, file_like_object=file_like_object)
        return instance

    def update(self, name, file_like_object=None):
        """
        Update value from file like object.

        Update properties, reading the ``file_like_object`` into
        ``self.value`` if provided.
        """
        self.name = name
        if file_like_object is not None:
            self.value = file_like_object.read()

    def update_from_url(self, url):
        """
        Update value from url's content.

        Update ``self.value`` to be the contents of the file downloaded
        from the ``url`` provided.
        """
        # Download the file, raising an exception if the download fails
        # after retrying once.
        attempts = 0
        max_attempts = 2
        while True:
            attempts += 1
            r = requests.get(url)
            if r.status_code == HTTPStatus.OK:
                break
            if attempts < max_attempts:
                continue
            r.raise_for_status()

        self.value = r.content

    def get_as_named_tempfile(self, should_close=False):
        """Read ``self.value`` into and return a named temporary file."""
        # Prepare the temp file.
        f = NamedTemporaryFile(delete=False)

        # Read self.value into it.
        if self.value is not None:
            f.write(self.value)

        # Close the file so its readable from the filename.
        if should_close:
            f.close()

        # Return the file.
        return f

    def __json__(self):
        """Create a JSONable representation."""
        return {"name": self.name}
