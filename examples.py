#!/usr/bin/env python

"""Markdown Grid Extension demo"""

import sys
import glob
import os.path
import markdown

# Extension module is imported for cases 2 and 3.
# It's not necessary for the first example.
import mdx_grid


for fname in glob.glob('./examples/*.md'):
    sys.stdout.write("Processing '%s'... " % os.path.basename(fname))

    # Case #1: Using default configuration (Twitter Bootstrap)
    md = markdown.Markdown(extensions=['grid'])
    md.convertFile(fname, output=fname + '.bootstrap.html', encoding='utf8')

    # Case #2: Using one of the predefined alternative configuration profiles
    config = mdx_grid.get_conf(mdx_grid.SKELETON_PROFILE)
    md = markdown.Markdown(extensions=['grid'],
                           extension_configs={'grid': config})
    md.convertFile(fname, output=fname + '.skeleton.html', encoding='utf8')

    # Case #3: Using custom extension configuration profile
    config = {
        'profile': 'custom',
        'row_open': '<div class="row">',
        'row_close': '</div>',
        'col_open': '<div class="{value} column">',
        'col_close': '</div>',
        'default_col': 'span6',
        'aliases': [
            (r"\b(\d+)\:(\d+)\b", r"span\1 offset\2"),
            (r"\b(\d+)\b", r"span\1"),
        ],
    }
    md = markdown.Markdown(extensions=['grid'],
                           extension_configs={'grid': config})
    md.convertFile(fname, output=fname + '.custom.html', encoding='utf8')

    print("Done.")
