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

# Predefined configuration profiles. Each profile is a dictionary
# containing the following values:
#  - profile -- Configuration profile name
#  - row_open -- Grid row opening
#  - row_close -- Grid row closing
#  - col_open -- Column opening
#  - col_close -- Column opening
#  - default_col_class -- Default column class
#  - col_class_first -- CSS class for the first column in the row
#  - col_class_last -- CSS class for the last column in the row
#  - aliases -- a dictionary of regular expressions used to shorten
#    CSS class names used in row declaration.
PROFILES = {
    BLANK_PROFILE: {
        'profile': '',
        'row_open': '',
        'row_close': '',
        'col_open': '',
        'col_close': '',
        'default_col_class': '',
        'col_class_first': '',
        'col_class_last': '',
        'aliases': [],
    },
    BOOTSTRAP_PROFILE: {
        'profile': BOOTSTRAP_PROFILE,
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class="{value}">',
        'col_close': '</div>',
        'default_col_class': 'span1',
        'aliases': [
            (r'\b(\d+)\:(\d+)\b', r'span\1 offset\2'),
            (r'\b(\d+)\b', r'span\1'),
        ],
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


ROW_OPEN_CMD = "row"
ROW_CLOSE_CMD = "endrow"
COL_OPEN_CMD = "col"
COL_CLOSE_CMD = "endcol"

RE_FLAGS = re.UNICODE | re.IGNORECASE | re.MULTILINE

# Grid markers
ROW_OPEN = re.compile(r"^\s*--\s*row\s*([\w,-\:\s]*)\s*--\s*$", flags=RE_FLAGS)
ROW_CLOSE = re.compile(r"^\s*--\s*end\s*--\s*$", flags=RE_FLAGS)
COL_SEP = re.compile(r"^\s*--\s*$", flags=RE_FLAGS)

# Grid tag - a container for command sequence
TAG = re.compile(r"\s*<!--grid\:(.*)-->\s*", flags=RE_FLAGS)
COMMAND = re.compile(r"(\w+)(?:\((.*)\))?")


def process_configuration(source_conf):
    """Gets a valid configuration profile.

    Arguments:
        source_conf -- a dictionary received from the consumer during
            extension configuration.

    Returns:
        The get_conf() result for specified profile with precompiled aliases.
        Custom configurations will be compementeds with undefined parameters."""

    # Complement the source configuration dictionary with undefined
    # parameters.
    conf = get_conf(BLANK_PROFILE)
    if not source_conf:
        conf.update(get_conf(DEFAULT_PROFILE))
    else:
        conf.update(source_conf)

    # Updates 'profile' parameter value to 'custom' if it's not
    # defined.
    if not conf['profile']:
        conf['profile'] = 'custom'

    # 'Aliases' is a list of replacements for --row-- marker arguments.
    # Each item contains a tuple of two items: a regex and a replacement
    # string itself. Regexes will be compiled for further usage.
    if not isinstance(conf['aliases'], list):
        conf['aliases'] = []
    elif conf['aliases']:
        cmpl = lambda a: (re.compile(a[0]), a[1])
        conf['aliases'] = [cmpl(a) for a in conf['aliases']]

    return conf


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
        return PROFILES[profile_name]
    except Exception as e:
        message = "Specified configuration profile not exists: '%s'."
        raise Exception(message % profile_name, e)


def expand_aliases(arg, aliases):
    for subj, repl in aliases:
        arg = subj.sub(repl, arg)
    return arg


def parse_row_args(arguments, aliases=[]):
    """Parses --row-- arguments from a string.

    Each row marker contains a set of parameters defining a list of CSS classes
    for the corresponding column. This function takes a comma-separated string
    and returns a list of processed values. If there are no arguments, an empty
    list will be returned.

    Arguments:
        arguments -- a string of comma-separated arguments. Each argument
            is a space-separated list of CSS class names or aliases
            to be be replaced with actual class names.
        aliases -- replacements list to be applied on the each argument.

    Usage:
        >>> parse_row_args("span4 offset4, span4, span2")
        ['span4 offset4', 'span4', 'span2']
        >>> parse_row_args("4:1, 4, 3", bootstrap_aliases)
        ['span4 offset1', 'span4', 'span3']"""

    args = [' '.join(arg.split()) for arg in str(arguments or '').split(',')]
    args = [] if len(args) == 1 and not args[0] else args
    return [expand_aliases(arg, aliases) for arg in args]


def get_tag(commands):
    """Generates a preprocessor tag from a set of grid commands."""
    # Extra line break prevents unclosed paragraphs in markdown HTML output
    return "\n<!--grid:%s-->" % ';'.join([str(cmd) for cmd in commands])


def replace_markers(lines, cmds):
    """Replace grid markers with tags.

    Arguments:
        lines -- source markdown text as a list of lines.
        cmds -- a dictionary mapping line numbers to lists of grid commands.

    Returns:
        An updated list with grid tags inserted against the markup."""

    for line_num in cmds:
        lines[line_num] = get_tag(cmds[line_num])
    return lines


def get_closure(row_stack):
    """Generate the terminating row/column grid tag to complement
    incompleted markup (if it's incompleted)."""
    closure = []
    while row_stack:
        closure.append(Command(COL_CLOSE_CMD))
        closure.append(Command(ROW_CLOSE_CMD))
        row_stack.pop()
    return closure


class Command:
    """Grid command representation."""
    # TODO: Consider to replace with tuples.

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

    def run(self, lines):
        """Main preprocessor method.

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
            matches = ROW_OPEN.match(line)
            if matches:  # <row [params]><col>
                row_stack.append(line_num)
                args = matches.group(1) if matches.groups() else ''
                rows[line_num] = parse_row_args(args, self.conf['aliases'])
                r2c[row_stack[-1]] = [line_num]
                cmds[line_num] = [Command(ROW_OPEN_CMD),
                                  Command(COL_OPEN_CMD)]

            elif ROW_CLOSE.match(line):  # </col></row>
                cmds[line_num] = [Command(COL_CLOSE_CMD),
                                  Command(ROW_CLOSE_CMD)]
                row_stack.pop()

            elif COL_SEP.match(line):  # </col><col>
                r2c[row_stack[-1]].append(line_num)
                cmds[line_num] = [Command(COL_CLOSE_CMD),
                                  Command(COL_OPEN_CMD)]

        # Adding style definition for <col>-s
        def_style = self.conf['default_col_class']
        for row_line_num in rows:
            styles = rows[row_line_num][::-1]
            for col_line_num in r2c[row_line_num]:
                for cmd in cmds[col_line_num]:
                    if cmd.value == COL_OPEN_CMD:
                        cmd.style = styles.pop() if styles else def_style
                        break

        result = replace_markers(lines, cmds)
        closure = get_closure(row_stack)
        return result + [get_tag(closure)] if closure else result


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
    #     matches = COMMAND.match(command)
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
        # return TAG.sub(GridPostprocessor.expand_tag, text)


class GridExtension(markdown.Extension):
    """Markdown extension class."""

    def __init__(self, configs):
        self.conf = {}
        self.conf = process_configuration(configs)

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
