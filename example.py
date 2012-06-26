#!/usr/bin/env python

"""Markdown Grid Extension demo"""

import codecs
import markdown
import mdx_grid


def save(file_name, text):
    with codecs.open(file_name, mode="w", encoding="utf8") as f:
        f.write(text)


def load(file_name):
    with codecs.open(file_name, mode="r", encoding="utf8") as f:
        return f.read()


# Case #1: Adding extension by name
text = load("example-1.md")
md = markdown.Markdown(extensions=['grid'])
save("example-1.html", md.convert(text))


# Case #2: Using existing extension instance with custom configuration
text = load("example-2.md")
gridext = mdx_grid.GridExtension(configs=mdx_grid.GridConf.SKELETON)
md = markdown.Markdown(extensions=[gridext])
save("example-2.html", md.convert(text))
