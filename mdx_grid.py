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

__author__ = "Alex Musayev"
__email__ = "alex.musayev@gmail.com"
__copyright__ = "Copyright 2012, %s <http://alex.musayev.com>" % __author__
__license__ = "MIT"
__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))
__status__ = "Development"
__url__ = "http://github.com/dreikanter/markdown-grid"


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

    # Syntax sugar to specify Bootstrap's span/offset classes
    re_spnoff = re.compile(r"(\d+)(\s*\:\s*(\d+))?")


class GridConf:
    """Extension configuration profiles container for common
    HTML/CSS frameworks.

    Configuration parameters:
      - row_open - Grid row opening
      - row_close - Grid row closing
      - col_open - Column opening
      - col_close - Column opening
      - col_class - CSS class(es) for the column; {width} marker will
            be replaced with width value from the markup
      - col_class_first - CSS class(es) for the first column in the row
      - col_class_last - CSS class(es) for the last column in the row

     [TBD]

    """

    BOOTSTRAP = {
        'name': 'bootstrap',
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class="%s">',
        'col_close': '</div>',
        'col_span_class': 'span%s',
        'col_offset_class': 'offset%s',
        'default_col_class': 'span1',
        'common_col_class': '',
        'col_class_first': '',
        'col_class_last': '',
    }

    SKELETON = {}

    GS960 = {}

    # Alias for default configuration
    DEFAULT = BOOTSTRAP


class Parsers:
    """Common helper functions."""

    DEFAULT_SEPARATOR = ','
    # SECONDARY_SEPARATOR = ':'

    @staticmethod
    def expand_shortcuts(arg, is_bs):
        """Expand span/offset shortcuts for bootstrap.

        Arguments:
          - arg - argument string to process.
          - is_bs - True if current configuration profile is Bootstrap.

        Usage:
            >>> expand_shortcuts('4:1', True)
            'span4 offset1'
            >>> expand_shortcuts('6', True)
            'span6'
            >>> expand_shortcuts('8', False)
            '8'
        """

        def expand(matches):
            s = matches.group(0)
            o = matches.group(3)
            return 'span' + str(s) + ((' offset' + o) if o else '')

        return Patterns.re_spnoff.sub(expand, arg) if is_bs else arg

    @staticmethod
    def parse_row_args(arguments, profile=None):
        """Parses --row-- arguments from a string.

        Each row marker contains a set of parameters defining CSS classes for
        the corresponding column. This function takes a comma-separated string
        and returns a list of processed values.

        Arguments:
          - arguments - comma-separated string of arguments.
          - profile   - configuration profile name which affects
                        framework-specific parsing options.

        Usage:
            >>> Parsers.parse_row_args("span4 offset4, span4, span2")
            ['span4 offset4', 'span4', 'span2']
            >>> Parsers.parse_row_args("4:1, 4, 3", profile='bootstrap')
            ['span4 offset1', 'span4', 'span3']

        """

        args = str(arguments).split(Parsers.DEFAULT_SEPARATOR)
        args = filter(None, [' '.join(arg.split()) for arg in args])
        is_bs = profile == GridConf.BOOTSTRAP['name']
        return [Parsers.expand_shortcuts(arg, is_bs) for arg in args]

    # @staticmethod
    # def parse_int(value, default=0):
    #     """Attempts to parse a positive integer from a string.
    #     Returns default value in case of parsing error or negative result."""

    #     try:
    #         return int(value)
    #     except:
    #         return default

    # @staticmethod
    # def parse_csints(csv_str, separator=DEFAULT_SEPARATOR):
    #     """Parses a string of comma-separated integers to a list."""
    #     return filter(lambda x: x != None, [Parsers.parse_int(x, None) for x in csv_str.split(separator)])

    # @staticmethod
    # def parse_spanoffset(value, separator=SECONDARY_SEPARATOR):
    #     """Parses coupled span:offset string and returns a list of two ints.
    #     If the offset is omitted, the second value will be zero."""
    #     result = value.split(separator)
    #     return [Parsers.parse_int(result[0], None), Parsers.parse_int(result[1]) if len(result) > 1 else 0]

    # @staticmethod
    # def parse_row_params(param_str, separator=DEFAULT_SEPARATOR):
    #     """Parses a row parameters string.

    #     Usage:
    #         >>> widths, offsets = parse_row_params('4, 2:2, 3:1')
    #         >>> widths
    #         [1, 2, 2]
    #         >>> offsets
    #         [0, 2, 1]



    #     """
    #     widths = []
    #     offsets = []

    #     def populate(span, offset):
    #         if span != None:
    #             widths.append(span)
    #             offsets.append(offset)

    #     map(lambda span_offset: populate(span_offset[0], span_offset[1]),
    #         [Parsers.parse_spanoffset(value) for value in param_str.split(separator)])

    #     return widths, offsets


class GridCmdInfo:
    """Grid command representation."""

    def __init__(self, cmdtype):
        self.cmdtype = cmdtype

    def __str__(self):
        """Generates text representation for a grid command."""
        is_col = self.cmdtype == GridCmd.COL_OPEN
        params = ("(%s)" % getattr(self, 'style', '')) if is_col else ''
        return GridCmd.get_name(self.cmdtype) + params


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    """Markdown preprocessor."""

    @staticmethod
    def parse_markers(lines, profile=None):
        """Parses mardown source.

        Arguments:
            - lines   - markdown source as a list of text lines.
            - profile - configuration profile name which affects
                        framework-specific parsing options.

        Returns:
            A three-item tuple:

            # 1. Rows mapping: row-marker-linenum => [column-widths[], column-offsets[]]
            1. Rows mapping: row marker line => [column CSS classes]
               (each item could contain a set of space-separated class names)
            2. Grid commands mapping: marker line => [grid commands]
            3. Row to column mapping: row marker line => [column lines]"""

        row_stack = []  # Rows stack. Each item contains row marker line number
        rows = {}  # Rows mapping (result tuple item 1)
        cmds = {}  # Commands mapping (2)
        r2c = {}  # Row to column mapping (3)

        for line_num in range(len(lines)):
            line = lines[line_num]

            # Processing grid markers
            matches = Patterns.row_open.match(line)
            if matches:
                # Got  --row [params]-- which means <row [params]><col>
                row_stack.append(line_num)

                # rows[line_num] = Parsers.parse_row_params(matches.group(0) if matches.groups() else "")
                args = matches.group(0) if matches.groups() else ""
                rows[line_num] = Parsers.parse_row_args(args)

                r2c[row_stack[-1]] = [line_num]
                cmds[line_num] = [GridCmdInfo(GridCmd.ROW_OPEN),
                                  GridCmdInfo(GridCmd.COL_OPEN)]

            elif Patterns.row_close.match(line):
                # Got -- which means </col></row>
                cmds[line_num] = [GridCmdInfo(GridCmd.COL_CLOSE),
                                  GridCmdInfo(GridCmd.ROW_CLOSE)]
                row_stack.pop()

            elif Patterns.col_sep.match(line):
                # Got --end-- which means </col><col>
                r2c[row_stack[-1]].append(line_num)
                cmds[line_num] = [GridCmdInfo(GridCmd.COL_CLOSE),
                                  GridCmdInfo(GridCmd.COL_OPEN)]

            else:
                # Other lines are irrelevant
                pass

        if row_stack:
            # TODO: Close columns and rows if the stack is not empty
            # cmds[-1].append(...)
            pass

        return rows, cmds, r2c

    @staticmethod
    def populate_cmd_params(rows, cmds, r2c, default_col_style=""):
        """Returns a line number to grid commands mapping."""
        for row_line_num in rows:
            # spans, offsets = rows[row_line_num]
            styles = rows[row_line_num]
            col_num = 0
            for col_line_num in r2c[row_line_num]:
                for cmd in cmds[col_line_num]:
                    if cmd.cmdtype == GridCmd.COL_OPEN:
                        try:
                            cmd.style = styles[col_num]
                            # cmd.span = spans[col_num]
                            # cmd.offset = offsets[col_num]
                        except:
                            cmd.style = default_col_style
                            # cmd.span = 1
                            # cmd.offset = 0
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

    def get_conf(self, key):
        if key in self.config:
            return self.config[key][0]
        else:
            return None

    def run(self, lines):
        """Main preprocessor method."""
        # TODO: Purify configuration

        rows, cmds, r2c = GridPreprocessor.parse_markers(lines)
        style = self.md.get_conf('default_col_style')
        cmds = GridPreprocessor.populate_cmd_params(rows, cmds, r2c, style)
        result = GridPreprocessor.replace_markers(lines, cmds)

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

    def __init__(self, configs):
        self.conf = GridConf.DEFAULT

        if configs:
            # Overriding default configuration
            self.conf.update(configs)

    def extendMarkdown(self, md, md_globals):
        """Initializes markdown extension components."""
        preprocessor = GridPreprocessor(md)
        preprocessor.conf = self.conf
        md.preprocessors.add('grid', preprocessor, '_begin')
        postprocessor = GridPostprocessor(md)
        postprocessor.conf = self.conf
        md.postprocessors.add('grid', postprocessor, '_end')


def makeExtension(configs=None):
    """Markdown extension initializer."""
    return GridExtension(configs=configs)
