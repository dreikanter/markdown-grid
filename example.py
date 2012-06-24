import codecs
import markdown
# from pprint import pprint
import mdx_grid

text = ""

with codecs.open("example.md", mode="r", encoding="utf8") as source:
    text = source.read()

configs = {}
gridext = mdx_grid.GridExtension(configs=configs)
md = markdown.Markdown(extensions=[gridext])
html = md.convert(text)
with codecs.open("example_custom.html", mode="w", encoding="utf8") as destination:
    destination.write(html)

md = markdown.Markdown(extensions=['grid'])
with codecs.open("example_defaults.html", mode="w", encoding="utf8") as destination:
    destination.write(html)

# print(html)
