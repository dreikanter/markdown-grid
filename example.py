#!/usr/bin/env python

"""Markdown Grid Extension demo"""

import sys
import glob
import os.path
import markdown
import mdx_grid
from pprint import pprint

for fname in glob.glob('./examples/*.md'):
    sys.stdout.write("Processing '%s'... " % os.path.basename(fname))

    # Case #1: Using default configuration (Twitter Bootstrap)
    md = markdown.Markdown(extensions=['grid'])
    md.convertFile(fname, output=fname + '.bootstrap.html', encoding='utf8')

    # Case #2: Using one of the predefined alternative configuration profiles
    md = markdown.Markdown(extensions=['grid'],
                           extension_configs={'grid': mdx_grid.GridConf.get_conf(mdx_grid.SKELETON_PROFILE)})
    md.convertFile(fname, output=fname + '.skeleton.html', encoding='utf8')

    # # Case #2: Using one of the predefined alternative configuration profiles
    # conf = mdx_grid.GridConf.get_profile(mdx_grid.SKELETON_PROFILE)
    # md = markdown.Markdown(extensions=['grid'],
    #                        extension_configs={'grid': conf})
    # md.convertFile(fname, output=fname + '.skeleton.html', encoding='utf8')

    # # Case #3: Using custom extension configuration profile
    # conf = {
    #     'row_open': '<div class="custom-row">',
    #     'row_close': '</div>',
    #     'col_open': '<div class="{value}">',
    #     'col_close': '</div>',
    #     'col_span_class': 'custom-span{value}',
    #     'col_offset_class': 'custom-offset{value}',
    #     'default_col_class': 'default-span',
    #     'common_col_class': 'common-col',
    #     'col_class_first': 'first',
    #     'col_class_last': 'last',
    # }
    # gridext = mdx_grid.GridExtension(configs=mdx_grid.SKELETON_PROFILE)
    # md = markdown.Markdown(extensions=['grid'],
    #                        extension_configs={'grid': conf})
    # md.convertFile(fname, output=fname + '.custom.html', encoding='utf8')

    print("Done.")
