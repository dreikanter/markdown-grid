"""
Grid Extension for Python-Markdown
==================================

A Python-Markdown extension for grid building. It provides minimal
and straightforward syntax to create multicolumn text layouts.

Usage:

    >>> import markdown
    >>> md = markdown.Markdown(extensions=['grid'])
    >>> md.convertFile('hello.md', output='hello.html', encoding='utf8')

    >>> conf = {'grid': mdx_grid.get_conf(mdx_grid.SKELETON_PROFILE)}
    >>> md = markdown.Markdown(extensions=['grid'], extension_configs=conf)
    >>> md.convertFile('hello.md', output='hello.html', encoding='utf8')

    >>> conf = {'grid': {'profile_name' : 'bootstrap3'}}
    >>> md = markdown.Markdown(extensions=['grid'], extension_configs=conf)
    >>> md.convertFile('hello.md', output='hello.html', encoding='utf8')

    See `example.py` for more usage examples.

Extension configuration:
    Each profile is a dictionary containing the following values:
     - profile -- Configuration profile name
     - row_open -- Grid row opening
     - row_close -- Grid row closing
     - col_open -- Column opening
     - col_close -- Column opening
     - default_col -- Default column class
     - first_col -- CSS class for the first column in the row
     - last_col -- CSS class for the last column in the row
     - aliases -- a dictionary of regular expressions used to shorten
       CSS class names used in row declaration.


Copyright 2012 [Alex Musayev](http://alex.musayev.com/)

Dependencies:
* [Python 2.6+](http://python.org)
* [Markdown 2.1+](http://www.freewisdom.org/projects/python-markdown/)

encoding: utf-8

"""

import re
import markdown


__author__ = 'Alex Musayev'
__email__ = 'alex.musayev@gmail.com'
__copyright__ = 'Copyright 2014, %s <http://alex.musayev.com>' % __author__
__license__ = 'MIT'
__version_info__ = (0, 2, 1)
__version__ = '.'.join(map(str, __version_info__))
__status__ = 'Development'
__url__ = 'http://github.com/dreikanter/markdown-grid'


# Extension configuration profile names
BOOTSTRAP_PROFILE = 'bootstrap'
BOOTSTRAP3_PROFILE = 'bootstrap3'
SKELETON_PROFILE = 'skeleton'
GS960_PROFILE = '960gs'

# Default configuration profile name. Will be used by the extension
# if custom configuration is not specified.
DEFAULT_PROFILE = BOOTSTRAP_PROFILE

# A complete sete of configuration parameters with no values.
# Used to complement user-defined profiles.
BLANK_PROFILE = 'blank'

# Predefined configuration profiles
PROFILES = {
    BLANK_PROFILE: {
        'profile': '',
        'row_open': '',
        'row_close': '',
        'col_open': '',
        'col_close': '',
        'default_col': '',
        'first_col': 'first',
        'last_col': 'last',
        'aliases': [],
    },
    BOOTSTRAP_PROFILE: {
        'profile': BOOTSTRAP_PROFILE,
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class="{value}">',
        'col_close': '</div>',
        'default_col': 'span1',
        'aliases': [
            (r"\b(\d+)\:(\d+)\b", r"span\1 offset\2"),
            (r"\b(\d+)\b", r"span\1"),
        ],
    },
    BOOTSTRAP3_PROFILE: {
        'profile': BOOTSTRAP3_PROFILE,
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class="{value}">',
        'col_close': '</div>',
        'default_col': 'col-sm-1',
        'aliases': [
            (r"\b(\d+)\:(\d+)\b", r"col-sm-\1 col-sm-offset-\2"),
            (r"\b(\d+)\b", r"col-sm-\1"),
        ],
    },
    SKELETON_PROFILE: {
        'profile': SKELETON_PROFILE,
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class="{value} columns">',
        'col_close': '</div>',
        'default_col': 'one',
        'first_col': 'alpha',
        'last_col': 'omega',
        'aliases': [
            # TODO: Consider to use replacement functions here
            (r"\:1\b", r"offset-by-one"),
            (r"\:2\b", r"offset-by-two"),
            (r"\:3\b", r"offset-by-three"),
            (r"\:4\b", r"offset-by-four"),
            (r"\:5\b", r"offset-by-five"),
            (r"\:6\b", r"offset-by-six"),
            (r"\:7\b", r"offset-by-seven"),
            (r"\:8\b", r"offset-by-eight"),
            (r"\:9\b", r"offset-by-nine"),
            (r"\:10\b", r"offset-by-ten"),
            (r"\:11\b", r"offset-by-eleven"),
            (r"\:12\b", r"offset-by-twelve"),
            (r"\:13\b", r"offset-by-thirteen"),
            (r"\:14\b", r"offset-by-fourteen"),
            (r"\:15\b", r"offset-by-fifteen"),
            (r"\b1\/3\b", r"one-third"),
            (r"\b2\/3\b", r"two-thirds"),
            (r"\b1\b", r"one"),
            (r"\b2\b", r"two"),
            (r"\b3\b", r"three"),
            (r"\b4\b", r"four"),
            (r"\b5\b", r"five"),
            (r"\b6\b", r"six"),
            (r"\b7\b", r"seven"),
            (r"\b8\b", r"eight"),
            (r"\b9\b", r"nine"),
            (r"\b10\b", r"ten"),
            (r"\b11\b", r"eleven"),
            (r"\b12\b", r"twelve"),
            (r"\b13\b", r"thirteen"),
            (r"\b14\b", r"fourteen"),
            (r"\b15\b", r"fifteen"),
            (r"\b16\b", r"sixteen"),
        ],
    },
    GS960_PROFILE: {
        'profile': GS960_PROFILE,
        'row_close': '<div class="clear"></div>',
        'col_open': '<div class="{value}">',
        'col_close': '</div>',
        'default_col': 'grid_1',
        'aliases': [
            (r"\b0\:(\d+)\:(\d+)\b", r"grid_\1 postfix_\2"),
            (r"\b(\d+)\:(\d+)\:0\b", r"prefix_\1 grid_\2"),
            (r"\b(\d+)\:(\d+)\:(\d+)\b", r"prefix_\1 grid_\2 postfix_\3"),
            (r"\b(\d+)\:(\d+)\b", r""),
            (r"\b\>(\d+)\b", r"push_\1"),
            (r"\b\<(\d+)\b", r"pull_\1"),
            (r"\b(\d+)\b", r"grid_\1"),
            (r"\ba\b", r"alpha"),
            (r"\bz\b", r"omega"),
            (r"", r""),
        ],
    },
}

# Grid commands
ROW_OPEN_CMD = 'row'
ROW_CLOSE_CMD = 'endrow'
COL_OPEN_CMD = 'col'
COL_CLOSE_CMD = 'endcol'

RE_FLAGS = re.UNICODE | re.IGNORECASE | re.MULTILINE

# Grid markers
ROW_OPEN = re.compile(r"^\s*--\s*row\s*([\w,-\:\s]*)\s*--\s*$", flags=RE_FLAGS)
ROW_CLOSE = re.compile(r"^\s*--\s*end\s*--\s*$", flags=RE_FLAGS)
COL_SEP = re.compile(r"^\s*--\s*$", flags=RE_FLAGS)

# Grid tag - a container for command sequence
TAG = re.compile(r"\s*<!--grid\:(.*)-->\s*", flags=RE_FLAGS)
COMMAND = re.compile(r"(\w+)(?:\((.*)\))?", flags=RE_FLAGS)


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

    # If there is 'profile_name' key, read rest of the configuration
    # with get_conf
    if "profile_name" in conf:
        conf.update(get_conf(conf["profile_name"]))

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
    """Grid command representation.

    Attributes:
        value -- defines the command type.
        style -- CSS class name(s) for HTML elements generated for the command.
        xstyle -- optional extra style(s) for the HTML elements. Used to keep
            additional CSS class names for the utmost columns in a row."""

    def __init__(self, value, xstyle=None):
        self.value = value
        xstyle = str(xstyle).lower() if xstyle else ''
        self.xstyle = xstyle

    def __str__(self):
        """Generates text representation for a grid command."""
        return self.value + self.get_params()

    def get_params(self):
        """Retruns a formatted parameters string for command
        instances string representation."""
        if self.value == COL_OPEN_CMD:
            style = getattr(self, 'style', '')
            xstyle = getattr(self, 'xstyle', '')
            return '(%s)' % (style + (xstyle and (' ' + xstyle)))

        else:
            return ''


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
            3. Row to column mapping: row marker line => [column opening lines]
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
                try:
                    r2c[row_stack[-1]] = [line_num]
                    cmds[line_num] = [Command(ROW_OPEN_CMD),
                                      Command(COL_OPEN_CMD, xstyle='first_col')]
                except:
                    # Ignoring incorrect marker sequences
                    # TODO: Consider to add debug logging here
                    pass

            elif ROW_CLOSE.match(line):  # </col></row>
                cmds[line_num] = [Command(COL_CLOSE_CMD),
                                  Command(ROW_CLOSE_CMD)]

                # Mark the last column in the row
                try:
                    ln = r2c[row_stack[-1]][-1]
                    for cmd in cmds[ln]:
                        if cmd.value == COL_OPEN_CMD:
                            cmd.xstyle = 'last_col'
                            break
                    row_stack.pop()
                except:
                    # Ignoring incorrect marker sequences
                    # TODO: Consider to add debug logging here
                    pass

            elif COL_SEP.match(line):  # </col><col>
                # if len(row_stack) and row_stack[-1] in r2c:
                try:
                    r2c[row_stack[-1]].append(line_num)
                    cmds[line_num] = [Command(COL_CLOSE_CMD),
                                      Command(COL_OPEN_CMD)]
                except:
                    # Ignoring incorrect marker sequences
                    # TODO: Consider to add debug logging here
                    pass

        # Adding style definition for <col>-s
        def_style = self.conf['default_col']

        for row_line in rows:
            styles = rows[row_line][::-1]
            for col_line in r2c[row_line]:

                for cmd in cmds[col_line]:
                    # Affect the first COL_OPEN_CMD in line
                    if cmd.value == COL_OPEN_CMD:
                        cmd.style = styles.pop() if styles else def_style
                        if cmd.xstyle:
                            cmd.xstyle = self.conf[cmd.xstyle]
                        break

        result = replace_markers(lines, cmds)
        closure = get_closure(row_stack)
        return result + [get_tag(closure)] if closure else result


class GridPostprocessor(markdown.postprocessors.Postprocessor):
    """Markdown postprocessor."""

    def expand_match(self, matches):
        """Expands matched grid tag to HTML.

        Arguments:
            commands -- a list of grid commands separated by semicolon."""
        commands = matches.group(1).split(';')
        return ''.join([self.expand_cmd(cmd) for cmd in commands])

    def expand_cmd(self, command):
        matches = COMMAND.match(command)
        if not matches:
            return ''

        cmd_name = matches.group(1)

        if cmd_name == ROW_OPEN_CMD:
            return self.conf['row_open']

        elif cmd_name == ROW_CLOSE_CMD:
            return self.conf['row_close']

        elif cmd_name == COL_OPEN_CMD:
            html = self.conf['col_open']
            classes = matches.group(2) if len(matches.groups()) > 1 else ''
            return html.format(value=classes)

        elif cmd_name == COL_CLOSE_CMD:
            return self.conf['col_close']

        else:
            raise Exception("Unknown command: '%s'" % str(cmd_name))

    def run(self, text):
        return TAG.sub(self.expand_match, text)


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
        postprocessor.conf = self.conf
        md.postprocessors.add('grid', postprocessor, '_end')


def makeExtension(configs=None):
    """Markdown extension initializer."""
    return GridExtension(configs=configs)
