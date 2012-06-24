"""
Grid Extension
===============

A Python-Markdown extension for grid building. It provides minimal
and straightforward syntax to create multicolumn text layouts.

Usage:

    >>> import markdown
    >>> print markdown.markdown('TBD', extensions=['grid'])
    [TBD]

Copyright 2012 [Alex Musayev](http://alex.musayev.com/)

Dependencies:
* [Python 2.6+](http://python.org)
* [Markdown 2.1+](http://www.freewisdom.org/projects/python-markdown/)

"""

import markdown


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        return [line.replace("<!--", "<!----") for line in lines]


class GridPostprocessor(markdown.postprocessors.Postprocessor):
    def run(self, text):
        return text.replace("-->", "---->")


class GridExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('grid', GridPreprocessor(md), '_begin')
        md.postprocessors.add('grid', GridPostprocessor(md), '_end')


def makeExtension(configs=None):
    return GridExtension(configs=configs)
