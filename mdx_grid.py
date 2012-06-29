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

encoding: utf-8

"""



import re
import markdown

from pprint import pprint

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

# A complete sete of configuration parameters with no values.
# Used to complement user-defined profiles.
BLANK_PROFILE = 'blank'

ROW_OPEN_CMD = "row"
ROW_CLOSE_CMD = "endrow"
COL_OPEN_CMD = "col"
COL_CLOSE_CMD = "endcol"


class Patterns:
    """Common regular expressions."""

    _flags = re.UNICODE | re.IGNORECASE | re.MULTILINE

    # Grid markers
    row_open = re.compile(r"^\s*--\s*row\s*([a-z\d,-_\:\s]*)\s*--\s*$",
                          flags=_flags)
    row_close = re.compile(r"^\s*--\s*end\s*--\s*$", flags=_flags)
    col_sep = re.compile(r"^\s*--\s*$", flags=_flags)

    # # Grid commands for postprocessor
    # row_open_cmd = re.compile(r"^\s*row\s*$", flags=_flags)
    # row_close_cmd = re.compile(r"^\s*endrow\s*$", flags=_flags)
    # col_open_cmd = re.compile(r"^\s*col\s*\(([\d\s\:,]+)\)\s*$", flags=_flags)
    # col_close_cmd = re.compile(r"^\s*endcol\s*$", flags=_flags)

    # Grid tag - a container for command sequence
    # TODO: Use ?: for the second group
    tag = re.compile(r"\s*<!--grid\:(.*)-->\s*", flags=_flags)

    command = re.compile(r"(\w+)(?:\((.*)\))?")

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
        default_col_class -- Default column class
        col_class_first -- CSS class for the first column in the row
        col_class_last -- CSS class for the last column in the row
        aliases -- a dictionary of regular expressions used to shorten
            CSS class names used in row declaration."""

    # Name for user-defined profiles.
    _custom = 'custom'

    # Predefined configuration profiles.
    _profiles = {
        BLANK_PROFILE: {
            'profile': '',
            'row_open': '',
            'row_close': '',
            'col_open': '',
            'col_close': '',
            'default_col_class': '',
            'col_class_first': '',
            'col_class_last': '',
            'aliases': {},
        },
        BOOTSTRAP_PROFILE: {
            'profile': BOOTSTRAP_PROFILE,
            'row_open': '<div class="row">',
            'row_close': '</div>',
            'col_open': '<div class="{value}">',
            'col_close': '</div>',
            'default_col_class': 'span1',
            'aliases': {
                r'^\s*(\d+)\s*$': r'span\1',
                r'^\s*(\d+)\s*\:\s*(\d+)\s*$': r'span\1 offset\2',
            },
        },
        # TODO: ...
        SKELETON_PROFILE: {
            'profile': SKELETON_PROFILE,
        },
        # TODO: ...
        GS960_PROFILE: {
            'profile': GS960_PROFILE,
        },
    }

    @staticmethod
    def process_configuration(source_conf):
        """Gets a valid configuration profile.

        Arguments:
            source_conf -- a dictionary received from the consumer during
                extension configuration."""

        # Complement the source configuration dictionary with undefined
        # parameters.
        conf = GridConf.get_conf(BLANK_PROFILE)
        if not source_conf:
            conf.update(GridConf.get_conf(DEFAULT_PROFILE))
        else:
            conf.update(source_conf)

        # Updates 'profile' parameter value to 'custom' if it's not
        # defined.
        if not conf['profile']:
            conf['profile'] = 'custom'

        # 'Aliases' is a replacements dictionary for <row> marker arguments.
        # During the configuration processing conf['aliases'] value
        # will be converted from {regex:replacement} dictionary to a list of
        # (compiled regex, replacement) tuples to simplify further usage.
        if not isinstance(conf['aliases'], dict):
            conf['aliases'] = []
        elif conf['aliases']:
            cmpl = lambda a: (re.compile(a), conf['aliases'][a])
            conf['aliases'] = [cmpl(alias) for alias in conf['aliases']]

        return conf

    @staticmethod
    def get_conf(profile_name=DEFAULT_PROFILE):
        """Gets unprocessed configuration profile.

        Arguments:
            profile_name -- predefined configuration profile name. *_PROFILE
                constants is strictly recomended to be used here.

        Returns:
            This function returns a configuration parameters dictionary
            intended to be used for extension configuration with predefined
            profiles."""

        try:
            return GridConf._profiles[profile_name]
        except Exception as e:
            message = "Specified configuration profile not exists: '%s'."
            raise Exception(message % profile_name, e)

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
            print(profile.keys())

            profile['profile'] = name
            profile['aliases'] = GridConf.compile_aliases(profile['aliases'])
            return profile
        except Exception as e:
            raise Exception("Error getting config profile: " + name, e)

    @staticmethod
    def compile_aliases(aliases):
        """Compiles the dictionary of regular expressions."""
        result = []
        for alias in aliases:
            result.append((re.compile(alias), aliases[alias]))
        return result

    @staticmethod
    def get_param(profile, param):
        """Gets a single configuration parameter
        for one ofpredefined profiles."""
        try:
            return GridConf._profiles[profile][param]
        except Exception as e:
            message = "Error getting config parameter %s.%s"
            raise Exception(message % (profile, param), e)

    @staticmethod
    def purify(config):
        """Complements user-specified configuration dict with unspecified
        parameters to keep configuration profile complete.

        Arguments:
            config -- custom configuration profile dictionary {param: value}.

        Returns:
            The original dictionary data completed with undefined parameters
            (if any) initialized with BLANK_PROFILE values.

            # If no configuration specified default will be returned instead
            # of a dictionary filled with blank values.

            In addition to the explicitly specified parameters,
            there always will be 'profile' containing the profile name."""

        # if not config:
        #     return GridConf.get_profile()

        profile = dict(GridConf._profiles[GridConf.BLANK_PROFILE])
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
            # TODO: Use aliases to expand class names
            return "span-offset"
            # sc = GridConf.get_param(BOOTSTRAP_PROFILE, 'col_span_class')
            # span = sc.format(value=matches.group(1))

            # oc = GridConf.get_param(BOOTSTRAP_PROFILE, 'col_offset_class')
            # offset = matches.group(3)

            # return (span + ' ' + oc.format(value=offset)) if offset else span

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


class Command:
    """Grid command representation."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        """Generates text representation for a grid command."""
        return self.value + self.get_params()

    def get_params(self):
        is_col = self.value == COL_OPEN_CMD
        return ('(%s)' % getattr(self, 'style', '')) if is_col else ''


class GridPreprocessor(markdown.preprocessors.Preprocessor):
    """Markdown preprocessor."""

    @staticmethod
    def parse(lines, profile=None):
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
            3. Row to column mapping: row marker line => [column lines]
            4. Closure commands - an additional set of """

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
                cmds[line_num] = [Command(ROW_OPEN_CMD),
                                  Command(COL_OPEN_CMD)]

            elif Patterns.row_close.match(line):
                # Got --end-- which means </col></row>
                cmds[line_num] = [Command(COL_CLOSE_CMD),
                                  Command(ROW_CLOSE_CMD)]
                row_stack.pop()

            elif Patterns.col_sep.match(line):
                # Got -- which means </col><col>
                r2c[row_stack[-1]].append(line_num)
                cmds[line_num] = [Command(COL_CLOSE_CMD),
                                  Command(COL_OPEN_CMD)]

            else:
                # Other lines are irrelevant
                pass

        closure = []
        # Closing columns and rows if the stack is still not empty
        while row_stack:
            closure.append(Command(COL_CLOSE_CMD))
            closure.append(Command(ROW_CLOSE_CMD))
            row_stack.pop()

        return rows, cmds, r2c, closure

    @staticmethod
    def populate_cmd_params(rows, cmds, r2c, def_style=""):
        """Returns a line number to grid commands mapping."""
        for row_line_num in rows:
            styles = rows[row_line_num][::-1]
            for col_line_num in r2c[row_line_num]:
                for cmd in cmds[col_line_num]:
                    if cmd.value == COL_OPEN_CMD:
                        cmd.style = styles.pop() if styles else def_style
                        break
        return cmds

    @staticmethod
    def get_tag(commands):
        """Generates a preprocessor tag from a set of grid commands."""
        # Extra line break prevents generation of unclosed paragraphs
        return "\n<!--grid:%s-->" % ';'.join([str(cmd) for cmd in commands])

    @staticmethod
    def replace_markers(lines, cmds):
        """Replace grid markers with tags."""
        for line in cmds:
            lines[line] = GridPreprocessor.get_tag(cmds[line])
        return lines

    def run(self, lines):
        """Main preprocessor method."""
        return lines
        profile = self.conf['profile']
        rows, cmds, r2c, closure = GridPreprocessor.parse(lines, profile)
        cmds = GridPreprocessor.populate_cmd_params(rows, cmds, r2c, self.conf['default_col_class'])
        result = GridPreprocessor.replace_markers(lines, cmds)
        if closure:
            result.append(GridPreprocessor.get_tag(closure))
        return result


class GridPostprocessor(markdown.postprocessors.Postprocessor):
    """Markdown postprocessor."""

    # @staticmethod
    # def get_html(command, get_conf):
    #     if command == ROW_OPEN_CMD:
    #         return get_conf('row_open')
    #     elif command == ROW_CLOSE_CMD:
    #         return get_conf('row_close')
    #     elif command == COL_OPEN_CMD:
    #         return get_conf('col_open')
    #     elif command == COL_CLOSE_CMD:
    #         return get_conf('col_close')
    #     else:
    #         raise Exception("Bad command name: '%s'" % str(command))

    # @staticmethod
    # def expand_cmd(command, get_conf):
    #     """Converts a single grid command to HTML.

    #     Usage:
    #         >>> expand_cmd("row")
    #         '<div class="row">'
    #         >>> expand_cmd("row")
    #         '<div class="row">'

    #         """
    #     matches = Patterns.command.match(command)
    #     if not matches or not matches.groups():
    #         return ''
    #     html = GridPreprocessor.get_html(matches.group(1), get_conf)
    #     if matches.group(2):
    #         args = matches.group(2).split(',')
    #         # if no args, add default_col_class
    #         # if first add 'col_class_first': '',
    #         # if last add 'col_class_last': '',
    #         # process each argument using aliases
    #         # 'aliases': {},
    #         html.format(value=' '.join(args))

    #     return html

    # @staticmethod
    # def expand_tag(matches):
    #     """Converts commands matched from a grid tag to HTML code."""
    #     if not matches.groups():
    #         return ''

    #     commands = matches.group(1).split(';')
    #     html = ''.join([GridPostprocessor.expand_cmd(cmd) for cmd in commands])
    #     return '\n%s\n' % html

    def run(self, text):
        return text
        # return Patterns.tag.sub(GridPostprocessor.expand_tag, text)


class GridExtension(markdown.Extension):
    """Markdown extension class."""

    def __init__(self, configs):
        self.conf = {}
        self.conf = GridConf.process_configuration(configs)
        print('------------')
        pprint(self.conf)
        print('------------')

    def extendMarkdown(self, md, md_globals):
        """Initializes markdown extension components."""
        preprocessor = GridPreprocessor(md)
        preprocessor.conf = self.conf
        md.preprocessors.add('grid', preprocessor, '_begin')
        postprocessor = GridPostprocessor(md)
        preprocessor.conf = self.conf
        md.postprocessors.add('grid', postprocessor, '_end')


def makeExtension(configs=None):
    """Markdown extension initializer."""
    return GridExtension(configs=configs)
