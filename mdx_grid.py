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


__status__ = "Development"


class GridTags:
    ROW_START = 0
    ROW_END = 1
    CELL_START = 2
    CELL_END = 3


class RowStack:
    """Stack for row items used to handle
    nested row/cell containers processing."""

    class RowInfo:
        def __init__(self, line_num, widths):
            """Initializes class instance with row starting tag 
            line number and a list of cell widths."""

            #  TODO
            self.line_num = 0
            self._widths = widths
            self._cur_cell_index = 0
            return

        def get_next_cell_width(self):
            """Enumerates through cell widths."""
            # TODO: Range checking; return None if out of range
            result = self._widths[self._cur_cell_index]
            self._cur_cell_index = self._cur_cell_index + 1
            return result

        def add_cell_tag(self, line_num):
            """Adds cell starting tag line number."""
            # TODO
            return

        def validate_widths(self, tags):
            """Validates if cell widths are valid."""
            # TODO
            return


    def __init__(self):
        return

    def add_cell_tag(self, cell_tag):
        # TODO
        return

    def push(self, line_num, widths):
        # TODO
        return

    def pop(self):
        # TODO
        return


class TagsList:
    """Grid tags collection."""

    class GridTagInfo:
        def __init__(self, tag_type, span=0, offset=0):
            self.type = tag_type
            self.span = span
            self.offset = offset

    # TODO: Implement enumeration

    def append(self, line_num, tag_type, span=0, offset=0):
        return

    def get_last_num():
        # TODO
        return None


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    """Markdown preprocessor."""

    flags = re.UNICODE | re.IGNORECASE | re.MULTILINE

    re_row_begin = re.compile(r"^\s*--\s*row\s*([\d\s,]*)\s*--\s*$", flags=GridPreprocessor.flags)
    re_row_end = re.compile(r"^\s*--\s*end\s*--\s*$", flags=GridPreprocessor.flags)
    re_cell_sep = re.compile(r"^\s*--\s*$", GridPreprocessor.flags)

    # TODO: Use better way to keep default tag values
    # TODO: Override defaults with configuration
    tag_row_start_str = ""
    tag_row_end_str = ""
    tag_cell_start_str = ""
    tag_cell_end_str = ""

    @staticmethod
    def parse_widths(widths_str):
        """Parses string of comma-separated int values to a list."""
        # TODO
        widths = []
        return widths

    @staticmethod
    def get_next_width(row_stack):
        # TODO
        return 1

    @staticmethod
    def get_tag(tag_type, span=None):
        """Returns layout tag for specified tag an span (for cells)."""
        # TODO
        return ""

    def run(self, lines):
        tags = TagsList()
        row_stack = RowStack()

        # Extracting grid tags
        for line_num in range(len(lines)):
            line = lines[line_num]

            matches = re_row_begin.match(line)
            if matches:
                # Got <row><cell>
                # TODO: Validate matches
                row_stack.push(line_num, matches.groups(1))
                tags.append(line_num, GridTags.ROW_START)
                tags.append(ridTagInfo(line_num, GridTags.CELL_START, row_stack.get_last_num())
                row_stack.add_cell_tag(tags.get_last_num())

            elif re_row_end.matches(line):
                # Got </cell></row>
                tags.append(line_num, GridTagrs.CELL_END)
                tags.append(line_num, GridTagrs.ROW_END)
                row_stack.validate_widths(tags)
                row_stack.pop()

            elif re_cell_sep.matches(line):
                # Got </cell><cell>
                tags.append(line_num, GridTags.CELL_END)
                tags.append(line_num, GridTags.CELL_START, row_stack.get_last_num())

            else:
                # Other lines are irrelevant
                pass

        # Populating lines with actual grid tags
        for tag in tags:
            lines[tag.line_num] = tag.get_tag()

        return lines


class GridPostprocessor(markdown.postprocessors.Postprocessor):
    """Markdown postprocessor."""

    def run(self, text):
        # TODO: Get HTML markup from configuration
        # TODO: Replace grid tags with HTML markup
        return text


class GridExtension(markdown.Extension):
    """Markdown extension class."""

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('grid', GridPreprocessor(md), '_begin')
        md.postprocessors.add('grid', GridPostprocessor(md), '_end')


def makeExtension(configs=None):
    """Markdown extension initializer."""
    return GridExtension(configs=configs)


#   1        2   3   4   5      6   7      8   9   10
# t {5,2,2 t | t | t } t {4,8 t | t {6,6 t | t } t }

# if first line or new row:
#     rows += new row
#     cur_row.push(rows[-1])
#     cur_cell = new cell
#     cur_row.add_cell(cur_cell)

# Задача: Заменить каждую строку в разметке на explicit tag.

# tags = []
# rs = []
# foreach line, num in lines:
#     switch line:
#         case row start:
#             widths = get_widths()
#             rs.push new row(num, widths)
#             tags.add(num, row-start)
#             tags.add(num, cell-start(rs.widths.next))
#         case cell split:
#             tags.add(num, cell-end)
#             tags.add(num, cell-start(rs.widths.next))
#         case row end:
#             tags.add(num, cell-end)
#             tags.add(num, row-end)
#             rs.current_row.validate_widths()
#             rs.pop()

# # got valid tags data

# foreach tag in tags:
#     lines[tag.get_num()] = tag.get_tag()