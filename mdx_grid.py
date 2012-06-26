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

# TODO: Drop after debugging
import os
import tempfile

__status__ = "Development"


class GridCmd:
    """Grid commands."""

    ROW_OPEN = 0
    ROW_CLOSE = 1
    COL_OPEN = 2
    COL_CLOSE = 3

    @staticmethod
    def get_name(cmdtype):
        if cmdtype == GridCmd.ROW_OPEN:
            return "row"

        elif cmdtype == GridCmd.ROW_CLOSE:
            return "endrow"

        elif cmdtype == GridCmd.COL_OPEN:
            return "col"

        elif cmdtype == GridCmd.COL_CLOSE:
            return "endcol"

        else:
            raise Exception("Unknown tag type specified.")


class Patterns:
    """Common regular expressions."""

    re_flags = re.UNICODE | re.IGNORECASE | re.MULTILINE

    # Grid markers
    row_open = re.compile(r"^\s*--\s*row\s*([\d\s,]*)\s*--\s*$", flags=re_flags)
    row_close = re.compile(r"^\s*--\s*end\s*--\s*$", flags=re_flags)
    col_sep = re.compile(r"^\s*--\s*$", flags=re_flags)

    # Grid commands for postprocessor
    row_open_cmd = re.compile(r"^\s*row\s*$", flags=re_flags)
    row_close_cmd = re.compile(r"^\s*endrow\s*$", flags=re_flags)
    col_open_cmd = re.compile(r"^\s*col\s*\(([\d\s\:,]+)\)\s*$", flags=re_flags)
    col_close_cmd = re.compile(r"^\s*endcol\s*$", flags=re_flags)

    # Grid tag - a container for command sequence
    tag = re.compile(r"\s*<!--grid\:(.*)-->\s*")


class GridConf:
    """Contains extension configuration for common HTML/CSS frameworks.
    Each configuration is a dictionary defining the following values:

     - row_open  - Grid row opening
     - row_close - Grid row closing
     - col_open  - Column opening
     - col_close - Column opening
     - col_class - CSS class(es) for the column; {width} marker will
                   be replaced with width value from the markup
     - col_class_first - CSS class(es) for the first column in the row
     - col_class_last - CSS class(es) for the last column in the row

     Example:
        MY_GRID = {
            'row_open': '<div class="row">',
            'row_close': '</div>',
            'col_open': '<div class="{}{col_classes}">',
            'col_close': '</div>',
            'col_width_class': 'column{width}',
            'col_span_class': 'column{width}',
            'col_class_first': 'first',
            'col_class_last': 'second',
        }
    """

    BOOTSTRAP = {
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class=>',
        'col_close': '',
        'col_class': '',
        'col_class_first': '',
        'col_class_last': '',
    }

    SKELETON = {}

    GS960 = {}


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


class GridCmdInfo:
    def __init__(self, cmdtype, params={}):
        self.cmdtype = cmdtype
        self.params = params

    def get_formatted_params(self):
        """Returns grid command params as a list of strings."""

        if self.cmdtype == GridCmd.COL_OPEN:
            params = [getattr(self, 'span', 1)]

            offset = getattr(self, 'offset', 0)
            if offset:
                params.append(offset)

            return [str(param) for param in params]

        else:
            return []

    def __str__(self):
        """Generates text representation for a grid command."""
        cmd = GridCmd.get_name(self.cmdtype)
        params = ','.join(self.get_formatted_params())
        return cmd + (("(%s)" % params) if params else "")


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    """Markdown preprocessor."""

    @staticmethod
    def parse_markers(lines):
        """Parses mardown source and returns collected data which is a tuple of three items:
            1. Rows mapping: row-marker-line-number => [column-widths[], column-offsets[]]
            2. Grid commands mapping: marker-line-number => [grid-commands-list]
            3. Row to column mapping: row-marker-line-number => [columns-line-numbers]"""

        row_stack = []  # Rows stack. Each item contains row marker line number
        rows = {}  # Rows mapping
        cmds = {}  # Commands mapping
        r2c = {}  # Row to column mapping

        for line_num in range(len(lines)):
            line = lines[line_num]

            # Processing grid markers
            matches = Patterns.row_open.match(line)
            if matches:
                # Got  --row [params]-- which means <row [params]><col>
                row_stack.append(line_num)
                rows[line_num] = Parsers.parse_row_params(matches.group(0) if matches.groups() else "")
                r2c[row_stack[-1]] = [line_num]
                cmds[line_num] = [GridCmdInfo(GridCmd.ROW_OPEN), GridCmdInfo(GridCmd.COL_OPEN)]

            elif Patterns.row_close.match(line):
                # Got -- which means </col></row>
                cmds[line_num] = [GridCmdInfo(GridCmd.COL_CLOSE), GridCmdInfo(GridCmd.ROW_CLOSE)]
                row_stack.pop()

            elif Patterns.col_sep.match(line):
                # Got --end-- which means </col><col>
                r2c[row_stack[-1]].append(line_num)
                cmds[line_num] = [GridCmdInfo(GridCmd.COL_CLOSE), GridCmdInfo(GridCmd.COL_OPEN)]

            else:
                # Other lines are irrelevant
                pass

        if row_stack:
            # TODO: Close columns and rows if the stack is not empty
            # lines.append(...)
            pass

        return rows, cmds, r2c

    @staticmethod
    def populate_cmd_params(rows, cmds, r2c):
        """Returns a line number to grid commands mapping."""
        for row_line_num in rows:
            spans, offsets = rows[row_line_num]
            col_num = 0
            for col_line_num in r2c[row_line_num]:
                for cmd in cmds[col_line_num]:
                    if cmd.cmdtype == GridCmd.COL_OPEN:
                        try:
                            cmd.span = spans[col_num]
                            cmd.offset = offsets[col_num]
                        except:
                            cmd.span = 1
                            cmd.offset = 0
                        finally:
                            col_num += 1

                        break

        return cmds

    @staticmethod
    def replace_markers(lines, cmds):
        """Replace grid markers with tags."""
        for line_num in cmds:
            tag_commands = ';'.join([str(command) for command in cmds[line_num]])

            # Extra line break prevents generation of unclosed paragraphs
            lines[line_num] = "\n<!--grid:%s-->" % tag_commands

        return lines

    def run(self, lines):
        """Main preprocessor method."""
        rows, tags, r2c = GridPreprocessor.parse_markers(lines)
        tags = GridPreprocessor.populate_cmd_params(rows, tags, r2c)
        result = GridPreprocessor.replace_markers(lines, tags)

        # TODO: Drop after debugging
        fd, file_name = tempfile.mkstemp('.txt', os.path.join(os.getcwd(), 'tmp_preprocessor-out_'))
        print("Preprocessor output: " + file_name)
        with os.fdopen(fd, 'wt') as f:
            f.write("\n".join(lines))

        return result


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
