#!/usr/bin/env python

from setuptools import setup


setup(
    name='mdx_grid',
    description='Grid Extension for Python-Markdown',
    version='0.2.2',
    license='MIT',
    author='Alex Musayev',
    author_email='alex.musayev@gmail.com',
    url='http://github.com/dreikanter/markdown-grid',
    long_description=open('README.md').read(),
    package_dir={'mdx_grid': '.'},
    py_modules=['mdx_grid'],
    platforms=['any'],
    install_requires=['markdown'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
