#!/usr/bin/env python

from setuptools import setup

# Note: It would be nice to have a single source of truth for the version; (it exists here and in
# fables/__init__.py). Here is a nice reference of different ways this can be achieved:
# https://packaging.python.org/guides/single-sourcing-package-version/
VERSION = '0.0.1'


setup(name='fables',
      version=VERSION,
      description='The (F)ile T(ables) library',
      packages=['fables'],
      install_requires=[
          'pandas==0.23.4',
          'chardet==3.0.4',
          'python-magic==0.4.15',
          'xlrd==1.2.0',
          'msoffcrypto-tool==4.6.4',
          'python-magic-bin==0.4.14;platform_system=="Windows"',
      ],
      zip_safe=True,
)
