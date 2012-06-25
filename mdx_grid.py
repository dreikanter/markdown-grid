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

import re
import markdown


class GridRow:
    def __init__(self, params):
        self.widths = []
        self.spans = []
        self.cells = []

    def add_cell(self, cell):
        return


# class GridCell:


class GridPreprocessor(markdown.preprocessors.Preprocessor):

    flags = re.UNICODE | re.IGNORECASE | re.MULTILINE
    re_rowb = re.compile(r"^\s*--\s*row\s*([\d\s,]*)\s*--\s*$", flags=flags)
    re_rowe = re.compile(r"^\s*--\s*end\s*--\s*$", flags=flags)
    re_sep = re.compile(r"^\s*--\s*$", flags)

    @staticmethod
    def matches(re, text):
        return re.match(text)

    def run(self, lines):
        rows = []
        cnt = 0
        blockstack = []
        blocks = []
        # blocks[0] contains everything
        # blockstack[-1] is current one
        for line in lines:
            if not cnt:
                blockstack.append(GridRow())
                blocks.append(blockstack[-1])
            if row begin
                blockstack.append(GridRow())



        #     else
        #         matches = re_rowb.match(line):
        #         if matches:
        #             matches.group(1)


        #       if cur
        #           cur. = new cell(widths)
        #       cells += cur
        #   elif (rowe or last_line) and (cur != none)
        #       cur = null
        #   elif sep
        # 
        #   else just text line
        #       if cur
        #           cur.lines += line
        #       else
        #           
            # cnt = cnt + 1
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
