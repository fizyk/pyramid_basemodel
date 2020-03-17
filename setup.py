#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from os.path import dirname, join as join_path
from setuptools import setup, find_packages


def _read(file_name):
    sock = open(file_name)
    text = sock.read()
    sock.close()
    return text


requirements = [
    "pyramid_tm",
    "pyramid",
    "requests",
    "slugify",
    "zope.interface",
    "zope.sqlalchemy",
    "SQLAlchemy",
]
if sys.version_info[0] == 2:
    # currently has py3 compat issues
    requirements.append("inflect")

setup(
    name="pyramid_basemodel",
    version="0.3.7",
    description="Global base classes for Pyramid SQLAlchemy applications.",
    author="James Arthur",
    author_email="username: thruflo, domain: gmail.com",
    url="http://github.com/thruflo/pyramid_basemodel",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license=_read("UNLICENSE").split("\n")[0],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
)
