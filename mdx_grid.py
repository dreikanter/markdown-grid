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

    # Grid markers
    row_open = re.compile(r"^\s*--\s*row\s*([\d\s,]*)\s*--\s*$", flags=re_flags)
    row_close = re.compile(r"^\s*--\s*end\s*--\s*$", flags=re_flags)
    col_sep = re.compile(r"^\s*-{2,}\s*$", flags=re_flags)

    # Grid tags for postprocessor
    rowtag_open = re.compile(r"^<!--\s*row\s*-->$", flags=re_flags)
    rowtag_close = re.compile(r"^<!--\s*endrow\s*-->$", flags=re_flags)
    coltag_open = re.compile(r"^<!--\s*col\s*\(([\d\s\:,]+)\)\s*-->$", flags=re_flags)
    coltag_close = re.compile(r"^<!--\s*endcol\s*-->$", flags=re_flags)


# class RowStack:
#     """Stack for row items used to handle nested row/col containers."""

#     class RowInfo:
#         """Text column collection representation. Each column could
#         have width and offset."""

#         def __init__(self, line_num, params_str):
#             """Initializes class instance with row starting tag
#             line number and a list of column widths."""

#             self.line_num = line_num
#             self._widths, self._offsets = Parsers.parse_param_str(params_str)
#             self._cur_col_index = 0

#         def get_next_col(self):
#             """Enumerates through column widths."""
#             if self._cur_col_index >= len(self._widths):
#                 return None
#             else:
#                 result = (self._widths[self._cur_col_index], self._offsets[self._cur_col_index])
#                 self._cur_col_index += 1
#                 return result

#         def add_col_tag(self, line_num):
#             """Adds column starting tag line number."""
#             # TODO
#             return

#         def validate_widths(self, tags):
#             """Validates if column widths are valid."""
#             # TODO
#             return

#         def get_grid_tag_params(self):
#             # TODO
#             return ""

#     def __init__(self):
#         return

#     def add_col_tag(self, col_tag):
#         # TODO
#         return

#     def push(self, line_num, widths):
#         # TODO
#         return

#     def pop(self):
#         # TODO
#         return


# class TagsList:
#     """Grid tags collection."""

#     class TagInfo:
#         def __init__(self, tag_type, line_num=0, span=0, offset=0):
#             self.line_num = line_num
#             self.tag_type = tag_type
#             self.span = span
#             self.offset = offset

#         def get_formatted_params(self):
#             """Returns grid tag params as formatted string."""
#             if self.tag_type == GridTags.COL_OPEN:
#                 return str(self.span) + ("," + str(self.offset)) if self.offset else ""
#             else:
#                 return ""

#         def get_tag(self):
#             """Generates a grid tag."""
#             tag = GridTags.get_name(self.tag_type)
#             params = self.get_formatted_params()
#             return "<!--%s%s-->" % (tag, ("(%s)" % params) if params else "")

#     def __init__(self):
#         self._items = []
#         self._index = -1

#     def __iter__(self):
#         return self

#     def __next__(self):
#         return next(self)

#     def next(self):
#         try:
#             result = self._items[self._index]
#             self._index += 1
#             return result

#         except IndexError:
#             raise StopIteration

#     def append(self, line_num, tag_type, span=0, offset=0):
#         self._items.append(TagsList.TagInfo(tag_type, line_num, span, offset))

#     def get_last_num(self):
#         return self._items[-1].line_num if self._items else None


class GridTagInfo:
    def __init__(self, tag_type, params={}):
        self.tag_type = tag_type
        self.params = params

    def get_formatted_params(self):
        """Returns grid tag params as formatted string."""
        if self.tag_type == GridTags.COL_OPEN:
            offset = str(getattr(self, 'offset', 0))
            return str(getattr(self, 'span', '')) + (',' + offset) if offset else ''
        else:
            return ""

    def get_tag(self):
        """Generates a grid tag."""
        tag = GridTags.get_name(self.tag_type)
        params = self.get_formatted_params()
        return "<!--%s%s-->" % (tag, ("(%s)" % params) if params else "")


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    """Markdown preprocessor."""

    @staticmethod
    def parse_markers(lines):
        """Parses mardown source and returns collected data which is a tuple of three items:
            1. Rows mapping: row-marker-line-number => [col-widths[], col-offsets[]]
            2. Tags mapping: col-marker-line-number => [grid-tags-list]
            3. Row to column mapping: row-marker-line-number => [nested-columns-line-numbers]"""

        row_stack = []  # Rows stack. Each item contains row marker line number
        rows = {}       # Rows mapping
        tags = {}       # Tags mapping
        r2c = {}        # Row to column mapping

        for line_num in range(len(lines)):
            line = lines[line_num]

            # Processing grid markers
            matches = Patterns.row_open.match(line)
            if matches:
                # Got  --row [params]-- which means <row [params]><col>
                row_stack.append(line_num)
                rows[line_num] = Parsers.parse_row_params(matches.group(0) if matches.groups() else "")
                r2c[row_stack[-1]] = [line_num]
                tags[line_num] = [GridTagInfo(GridTags.ROW_OPEN), GridTagInfo(GridTags.COL_OPEN)]

            elif Patterns.row_close.match(line):
                # Got -- which means </col></row>
                tags[line_num] = [GridTagInfo(GridTags.COL_CLOSE), GridTagInfo(GridTags.ROW_CLOSE)]
                row_stack.pop()

            elif Patterns.col_sep.match(line):
                # Got --end-- which means </col><col>
                r2c[row_stack[-1]].append(line_num)
                tags[line_num] = [GridTagInfo(GridTags.COL_CLOSE), GridTagInfo(GridTags.COL_OPEN)]

            else:
                # Other lines are irrelevant
                pass

        if row_stack:
            # TODO: Close columns and rows if the stack is not empty
            # lines.append(...)
            pass

        return rows, tags, r2c

    @staticmethod
    def populate_tag_params(rows, tags, r2c):
        """Returns a line number to grid tags mapping."""
        for row_line_num in rows:
            spans, offsets = rows[row_line_num]
            col_num = 0
            for col_line_num in r2c[row_line_num]:
                for tag in tags[col_line_num]:
                    if tag.tag_type == GridTags.COL_OPEN:
                        try:
                            tag.span = spans[col_num]
                            tag.offset = offsets[col_num]
                        except:
                            tag.span = 1
                            tag.offset = 0
                        finally:
                            col_num += 1

                        break

        return tags

    @staticmethod
    def replace_markers(lines, tags):
        """Replace grid markers with tags."""
        for line_num in tags:
            lines[line_num] = ''.join([tag.get_tag() for tag in tags[line_num]])
        return lines

    def run(self, lines):
        """Main preprocessor method."""
        rows, tags, r2c = GridPreprocessor.parse_markers(lines)
        tags = GridPreprocessor.populate_tag_params(rows, tags, r2c)
        return GridPreprocessor.replace_markers(lines, tags)


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
