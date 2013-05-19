#!/usr/bin/env python

import sys
from setuptools import setup
import mdx_grid

setup(
    name=mdx_grid.__name__,
    description=mdx_grid.__doc__,
    version=mdx_grid.__version__,
    license=mdx_grid.__license__,
    author=mdx_grid.__author__,
    author_email=mdx_grid.__email__,
    url=mdx_grid.__url__,
    long_description=open('README.md').read(),
    package_dir={'mdx_grid': '.'},
    py_modules=['mdx_grid'],
    platforms=['any'],
    install_requires=[
        'markdown',
    ],
)
