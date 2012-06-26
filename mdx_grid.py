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
    ROW_OPEN = 0
    ROW_CLOSE = 1
    COL_OPEN = 2
    COL_CLOSE = 3

    @staticmethod
    def get_name(tag_type):
        if tag_type == GridTags.ROW_OPEN:
            return "row"

        elif tag_type == GridTags.ROW_CLOSE:
            return "endrow"

        elif tag_type == GridTags.COL_OPEN:
            return "col"

        elif tag_type == GridTags.COL_CLOSE:
            return "endcol"

        else:
            raise Exception("Unknown tag type specified.")


class Parsers:
    """Common helper functions."""

    DEFAULT_SEPARATOR = ','
    SECONDARY_SEPARATOR = ':'

    @staticmethod
    def parse_int(value, default=0):
        """Attempts to parse a positive integer from a string.
        Returns default value in case of parsing error or negative result."""
        try:
            return int(value)
        except:
            return default

    @staticmethod
    def parse_csints(csv_str, separator=DEFAULT_SEPARATOR):
        """Parses a string of comma separated integers to a list."""
        return filter(lambda x: x != None, [Parsers.parse_int(x, None) for x in csv_str.split(separator)])

    @staticmethod
    def parse_spanoffset(value, separator=SECONDARY_SEPARATOR):
        """Parses coupled span:offset string and returns a list of two ints.
        If the offset is omitted, the second value will be zero."""
        result = value.split(separator)
        return [Parsers.parse_int(result[0], None), Parsers.parse_int(result[1]) if len(result) > 1 else 0]

    @staticmethod
    def parse_row_params(param_str, separator=DEFAULT_SEPARATOR):
        """Parses a row parameters string.

        >>> widths, offsets = parse_row_params('4, 2:2, 3:1')
        >>> widths
        [1, 2, 2]
        >>> offsets
        [0, 2, 1]
        """
        widths = []
        offsets = []

        def populate(span, offset):
            if span != None:
                widths.append(span)
                offsets.append(offset)

        map(lambda span_offset: populate(span_offset[0], span_offset[1]),
            [Parsers.parse_spanoffset(value) for value in param_str.split(separator)])

        return widths, offsets


class Patterns:
    """Common regular expressions."""

    re_flags = re.UNICODE | re.IGNORECASE | re.MULTILINE

    # Extended Markdown syntax
    row_open = re.compile(r"^\s*--\s*row\s*([\d\s,]*)\s*--\s*$", flags=re_flags)
    row_close = re.compile(r"^\s*--\s*end\s*--\s*$", flags=re_flags)
    col_sep = re.compile(r"^\s*--\s*$", flags=re_flags)

    # Grid tags for postprocessor
    rowtag_open = re.compile(r"^<!--\s*row\s*-->$", flags=re_flags)
    rowtag_close = re.compile(r"^<!--\s*endrow\s*-->$", flags=re_flags)
    coltag_open = re.compile(r"^<!--\s*col\s*\(([\d\s\:,]+)\)\s*-->$", flags=re_flags)
    coltag_close = re.compile(r"^<!--\s*endcol\s*-->$", flags=re_flags)


class RowStack:
    """Stack for row items used to handle nested row/col containers."""

    class RowInfo:
        """Text column collection representation. Each column could
        have width and offset."""

        def __init__(self, line_num, params_str):
            """Initializes class instance with row starting tag
            line number and a list of column widths."""

            self.line_num = line_num
            self._widths, self._offsets = Parsers.parse_param_str(params_str)
            self._cur_col_index = 0

        def get_next_col(self):
            """Enumerates through column widths."""
            if self._cur_col_index >= len(self._widths):
                return None
            else:
                result = (self._widths[self._cur_col_index], self._offsets[self._cur_col_index])
                self._cur_col_index += 1
                return result

        def add_col_tag(self, line_num):
            """Adds column starting tag line number."""
            # TODO
            return

        def validate_widths(self, tags):
            """Validates if column widths are valid."""
            # TODO
            return

        def get_grid_tag_params(self):
            # TODO
            return ""

    def __init__(self):
        return

    def add_col_tag(self, col_tag):
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

    class TagInfo:
        def __init__(self, tag_type, line_num=0, span=0, offset=0):
            self.line_num = line_num
            self.tag_type = tag_type
            self.span = span
            self.offset = offset

        def get_formatted_params(self):
            """Returns grid tag params as formatted string."""
            if self.tag_type == GridTags.COL_OPEN:
                return str(self.span) + ("," + str(self.offset)) if self.offset else ""
            else:
                return ""

        def get_tag(self):
            """Generates a grid tag."""
            tag = GridTags.get_name(self.tag_type)
            params = self.get_formatted_params()
            return "<!--%s%s-->" % (tag, ("(%s)" % params) if params else "")

    def __init__(self):
        self._items = []
        self._index = -1

    def __iter__(self):
        return self

    def __next__(self):
        return next(self)

    def next(self):
        try:
            result = self._items[self._index]
            self._index += 1
            return result

        except IndexError:
            raise StopIteration

    def append(self, line_num, tag_type, span=0, offset=0):
        self._items.append(TagsList.TagInfo(tag_type, line_num, span, offset))

    def get_last_num(self):
        return self._items[-1].line_num if self._items else None


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    """Markdown preprocessor."""

    def run(self, lines):
        tags = TagsList()
        row_stack = RowStack()

        # Extracting grid tags
        for line_num in range(len(lines)):
            line = lines[line_num]

            matches = Patterns.row_open.match(line)
            if matches:
                # Got <row [params]><col>
                # row_info = line_num, parse(row_parms)
                # rows.push(row_info)
                # rows.current.add_col(line_num)
                # tags.append(line_num, row_open)
                # tags.append(line_num, col_open)
                row_stack.push(line_num, matches.group(0) if matches.groups() else None)
                tags.append(line_num, GridTags.ROW_OPEN)
                tags.append(line_num, GridTags.COL_OPEN, row_stack.get_last_num())
                row_stack.add_col_tag(tags.get_last_num())

            elif Patterns.row_close.matches(line):
                # Got </col></row>
                # rows.current.populate_params - set span+offset for each col_open tag with line_num saved to the rows.current
                # rows.pop
                # tags.append(line_numm col_close)
                # tags.append(line_numm row_close)
                tags.append(line_num, GridTags.COL_CLOSE)
                tags.append(line_num, GridTags.ROW_CLOSE)
                row_stack.validate_widths(tags)
                row_stack.pop()

            elif Patterns.col_sep.matches(line):
                # Got </col><col>
                # rows.current.add_col(line_num)
                # tags.append(line_num, col_close)
                # tags.append(line_num, col_open)
                tags.append(line_num, GridTags.COL_CLOSE)
                tags.append(line_num, GridTags.COL_OPEN, row_stack.get_last_num())

            else:
                # Other lines are irrelevant
                pass

        # Populating lines with actual grid tags
        for tag in tags:
            lines[tag.line_num] = tag.get_tag()

        # TODO: Close columns and rows if the stack is not empty
        # lines.append(...)

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
