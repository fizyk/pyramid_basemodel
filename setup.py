#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    "python-slugify",
    "zope.interface",
    "zope.sqlalchemy",
    "SQLAlchemy",
    "inflect",
]

test_requires = [
    "pytest",
    "pytest-cov",
    "pytest-xdist",
    "mock",
]

extras_require = {
    'tests': test_requires,
}


setup(
    name="pyramid_basemodel",
    version="0.4.0",
    description="Global base classes for Pyramid SQLAlchemy applications.",
    author="James Arthur",
#    author_email="username: thruflo, domain: gmail.com",
    maintainer="Grzegorz Śliwiński",
    maintainer_email="fizyk+pypi@fizyk.net.pl",
    url="http://github.com/thruflo/pyramid_basemodel",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
    extras_require=extras_require
)
