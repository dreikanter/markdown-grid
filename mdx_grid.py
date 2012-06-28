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

__author__ = "Alex Musayev"
__email__ = "alex.musayev@gmail.com"
__copyright__ = "Copyright 2012, %s <http://alex.musayev.com>" % __author__
__license__ = "MIT"
__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))
__status__ = "Development"
__url__ = "http://github.com/dreikanter/markdown-grid"


# Extension configuration profile names
BOOTSTRAP_PROFILE = 'bootstrap'
SKELETON_PROFILE = 'skeleton'
GS960_PROFILE = '960gs'

# Default configuration profile name. Will be used by the extension
# if custom configuration is not specified.
DEFAULT_PROFILE = BOOTSTRAP_PROFILE


class GridCmd:
    """Grid commands."""

    ROW_OPEN = 0
    ROW_CLOSE = 1
    COL_OPEN = 2
    COL_CLOSE = 3

    _names = {
        ROW_OPEN: "row",
        ROW_CLOSE: "endrow",
        COL_OPEN: "col",
        COL_CLOSE: "endcol",
    }

    @staticmethod
    def get_name(cmdtype):
        try:
            return GridCmd._names[cmdtype]
        except:
            raise Exception("Unknown tag type specified.")


class Patterns:
    """Common regular expressions."""

    _flags = re.UNICODE | re.IGNORECASE | re.MULTILINE

    # Grid markers
    row_open = re.compile(r"^\s*--\s*row\s*([a-z\d,-_\:\s]*)\s*--\s*$",
                          flags=_flags)
    row_close = re.compile(r"^\s*--\s*end\s*--\s*$", flags=_flags)
    col_sep = re.compile(r"^\s*--\s*$", flags=_flags)

    # Grid commands for postprocessor
    row_open_cmd = re.compile(r"^\s*row\s*$", flags=_flags)
    row_close_cmd = re.compile(r"^\s*endrow\s*$", flags=_flags)
    col_open_cmd = re.compile(r"^\s*col\s*\(([\d\s\:,]+)\)\s*$", flags=_flags)
    col_close_cmd = re.compile(r"^\s*endcol\s*$", flags=_flags)

    # Grid tag - a container for command sequence
    tag = re.compile(r"\s*<!--grid\:(.*)-->\s*", flags=_flags)

    # Syntax sugar to specify Bootstrap's span/offset classes
    re_spnoff = re.compile(r"^\s*(\d+)(\s*\:\s*(\d+))?\s*$")


class GridConf:
    """Predefined configuration profiles for common HTML/CSS frameworks.

    Configuration parameters:
        profile -- Configuration profile name
        row_open -- Grid row opening
        row_close -- Grid row closing
        col_open -- Column opening
        col_close -- Column opening
        col_span_class -- Column class. {value} marker will be replaced
            with span/width value from the markup
        col_offset_class -- Column offset class. {value} marker will be
            replaced with span/width value from the markup
        default_col_class -- Default column class
        common_col_class -- Common column class
        col_class_first -- CSS class for the first column in the row
        col_class_last -- CSS class for the last column in the row"""

    # A complete sete of configuration parameters with no values.
    # Used to complement user-defined profiles.
    _blank = 'blank'

    # Name for user-defined profiles.
    _custom = 'custom'

    # Predefined configuration profiles.
    _profiles = {
        _blank: {
            'row_open': '',
            'row_close': '',
            'col_open': '',
            'col_close': '',
            'col_span_class': '',
            'col_offset_class': '',
            'default_col_class': '',
            'common_col_class': '',
            'col_class_first': '',
            'col_class_last': '',
        },
        BOOTSTRAP_PROFILE: {
            'row_open': '<div class="row">',
            'row_close': '</div>',
            'col_open': '<div class="{value}">',
            'col_close': '</div>',
            'col_span_class': 'span{value}',
            'col_offset_class': 'offset{value}',
            'default_col_class': 'span1',
            'common_col_class': '',
            'col_class_first': '',
            'col_class_last': '',
        },
        # TODO: ...
        SKELETON_PROFILE: {},
        # TODO: ...
        GS960_PROFILE: {},
    }

    @staticmethod
    def get_profile(name=None):
        """Gets predefined configuration profile specified by name.

        Arguments:
            name -- one of the standard profile names. It's recomended
                to use *_PROFILE constants here against string values.

        Returns:
            Extension configuration dictionary."""

        name = str(name) if name else DEFAULT_PROFILE

        try:
            profile = dict(GridConf._profiles[name])
            profile['profile'] = name
            return profile
        except Exception as e:
            raise Exception("Error getting config profile: " + name, e)

    @staticmethod
    def get_param(profile, param):
        """Gets a single configuration parameter
        for one ofpredefined profiles."""
        try:
            return GridConf._profiles[profile][param]
        except:
            raise Exception("Error getting config " \
                "parameter '%s.%s'" % (profile, param))

    @staticmethod
    def purify(config):
        """Complements user-specified configuration dict with unspecified
        parameters to keep configuration profile complete.

        Arguments:
            config -- custom configuration profile dictionary {param: value}.

        Returns:
            The original dictionary data completed with undefined parameters
            (if any) initialized with _blank values.

            If no configuration specified default will be returned instead
            of a dictionary filled with blank values.

            In addition to the explicitly specified parameters,
            there always will be 'profile' containing the profile name."""

        if not config:
            return GridConf.get_profile()

        profile = dict(GridConf._profiles[GridConf._blank])
        profile.update(dict(config))
        profile['profile'] = GridConf._custom

        return profile


class Parsers:
    """Common helper functions."""

    DEFAULT_SEPARATOR = ','

    @staticmethod
    def expand_shortcuts(arg, is_bs):
        """Expand span/offset shortcuts for bootstrap.

        Arguments:
            arg -- argument string to process.
            is_bs -- True if current configuration profile is Bootstrap.

        Usage:
            >>> expand_shortcuts('4:1', True)
            'span4 offset1'
            >>> expand_shortcuts('6', True)
            'span6'
            >>> expand_shortcuts('8', False)
            '8'
        """

        def expand(matches):
            """Expands a single span:offset group."""
            sc = GridConf.get_param(BOOTSTRAP_PROFILE, 'col_span_class')
            span = sc.format(value=matches.group(1))

            oc = GridConf.get_param(BOOTSTRAP_PROFILE, 'col_offset_class')
            offset = matches.group(3)

            return (span + ' ' + oc.format(value=offset)) if offset else span

        return Patterns.re_spnoff.sub(expand, arg) if is_bs else arg

    @staticmethod
    def parse_row_args(arguments, profile=None):
        """Parses --row-- arguments from a string.

        Each row marker contains a set of parameters defining CSS classes for
        the corresponding column. This function takes a comma-separated string
        and returns a list of processed values. If there are no values, an empty
        list will be returned.

        Arguments:
            arguments -- comma-separated string of arguments.
            profile -- configuration profile name which affects
                framework-specific parsing options.

        Usage:
            >>> Parsers.parse_row_args("span4 offset4, span4, span2")
            ['span4 offset4', 'span4', 'span2']
            >>> Parsers.parse_row_args("4:1, 4, 3", profile='bootstrap')
            ['span4 offset1', 'span4', 'span3']

        """

        args = str(arguments).split(Parsers.DEFAULT_SEPARATOR)
        args = [' '.join(arg.split()) for arg in args]
        if len(args) == 1 and not args[0]:
            args = []
        is_bs = (profile == 'bootstrap')
        return [Parsers.expand_shortcuts(arg, is_bs) for arg in args]


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
            lines -- markdown source as a list of text lines.
            profile -- configuration profile name which affects
                framework-specific parsing options.

        Returns:
            A three-item tuple:

            1. Rows mapping: row marker line => [column CSS classes]
               (each item could contain a set of space-separated class names)
            2. Grid commands mapping: marker line => [grid commands]
            3. Row to column mapping: row marker line => [column lines]"""

        row_stack = []  # Rows stack. Each item contains row marker line number
        rows = {}       # Rows mapping (first item from the result tuple)
        cmds = {}       # Commands mapping (second one)
        r2c = {}        # Row to column mapping (third)

        for line_num in range(len(lines)):
            line = lines[line_num]

            # Processing grid markers
            matches = Patterns.row_open.match(line)
            if matches:
                # Got  --row [params]-- which means <row [params]><col>
                row_stack.append(line_num)
                args = matches.group(1) if matches.groups() else ""
                rows[line_num] = Parsers.parse_row_args(args, profile)
                r2c[row_stack[-1]] = [line_num]
                cmds[line_num] = [GridCmdInfo(GridCmd.ROW_OPEN),
                                  GridCmdInfo(GridCmd.COL_OPEN)]

            elif Patterns.row_close.match(line):
                # Got --end-- which means </col></row>
                cmds[line_num] = [GridCmdInfo(GridCmd.COL_CLOSE),
                                  GridCmdInfo(GridCmd.ROW_CLOSE)]
                row_stack.pop()

            elif Patterns.col_sep.match(line):
                # Got -- which means </col><col>
                r2c[row_stack[-1]].append(line_num)
                cmds[line_num] = [GridCmdInfo(GridCmd.COL_CLOSE),
                                  GridCmdInfo(GridCmd.COL_OPEN)]

            else:
                # Other lines are irrelevant
                pass

        if row_stack:
            # Closing columns and rows if the stack is still not empty
            while row_stack:
                cmds[max(cmds.keys())].append([GridCmdInfo(GridCmd.COL_CLOSE),
                                               GridCmdInfo(GridCmd.ROW_CLOSE)])
                row_stack.pop()

        # TODO: Fix this:
        #   (u'endcol;col(None)',)
        #   (u'endcol;endrow;[<mdx_grid.GridCmdInfo instance at 0x023E05A8>, <mdx_grid.GridCmdInfo instance at 0x023E05D0>]',)

        return rows, cmds, r2c

    @staticmethod
    def populate_cmd_params(rows, cmds, r2c, def_col_style=""):
        """Returns a line number to grid commands mapping."""
        for row_line_num in rows:
            styles = rows[row_line_num][::-1]
            for col_line_num in r2c[row_line_num]:
                for cmd in cmds[col_line_num]:
                    if cmd.cmdtype == GridCmd.COL_OPEN:
                        cmd.style = styles.pop() if styles else def_col_style
                        break
        return cmds

    @staticmethod
    def replace_markers(lines, cmds):
        """Replace grid markers with tags."""
        for line_num in cmds:
            commands = [str(command) for command in cmds[line_num]]
            commands = ';'.join(commands)

            # Extra line break prevents generation of unclosed paragraphs
            lines[line_num] = "\n<!--grid:%s-->" % commands

        return lines

    def run(self, lines):
        """Main preprocessor method."""
        profile = self.get_conf('profile')
        rows, cmds, r2c = GridPreprocessor.parse_markers(lines, profile)
        style = self.get_conf('default_col_style')
        cmds = GridPreprocessor.populate_cmd_params(rows, cmds, r2c, style)
        result = GridPreprocessor.replace_markers(lines, cmds)
        return result


class GridPostprocessor(markdown.postprocessors.Postprocessor):
    """Markdown postprocessor."""

    @staticmethod
    def markup(command):
        # TODO: Process commands
        # TODO: Unittest
        return '<%s>' % command

    @staticmethod
    def expand_tag(matches):
        # TODO: Unittest
        if not matches.groups():
            return ''

        commands = matches.group(1).split(';')
        html = ''.join([GridPostprocessor.markup(cmd) for cmd in commands])
        return html

    def run(self, text):
        return Patterns.tag.sub(GridPostprocessor.expand_tag, text)


class GridExtension(markdown.Extension):
    """Markdown extension class."""

    def __init__(self, configs):
        if isinstance(configs, list):
            self.config = GridConf.purify(configs)
        else:
            self.config = GridConf.get_profile(configs)

    def extendMarkdown(self, md, md_globals):
        """Initializes markdown extension components."""
        preprocessor = GridPreprocessor(md)
        preprocessor.get_conf = self.get_conf
        md.preprocessors.add('grid', preprocessor, '_begin')
        postprocessor = GridPostprocessor(md)
        preprocessor.get_conf = self.get_conf
        md.postprocessors.add('grid', postprocessor, '_end')

    def get_conf(self, key):
        """Gets configuration parameter value."""
        if key in self.config:
            return self.config[key]
        else:
            return None


def makeExtension(configs=None):
    """Markdown extension initializer."""
    return GridExtension(configs=configs)
