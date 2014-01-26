#!/usr/bin/env python

import sys
from setuptools import setup


setup(
    name='mdx_grid',
    description='Grid Extension for Python-Markdown',
    version='0.2.1',
    license='MIT',
    author='Alex Musayev',
    author_email='alex.musayev@gmail.com',
    url='http://github.com/dreikanter/markdown-grid',
    long_description=open('README.md').read(),
    package_dir={'mdx_grid': '.'},
    py_modules=['mdx_grid'],
    platforms=['any'],
    install_requires=[
        'markdown',
    ],
)
