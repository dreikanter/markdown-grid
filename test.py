import codecs
import markdown
from pprint import pprint

text = ""

with codecs.open("index.md", mode="r", encoding="utf8") as source:
    text = source.read()

md = markdown.Markdown(extensions = ['nl2br', 'meta'])
html = md.convert(text)
    
with codecs.open("index.html", mode="w", encoding="utf8") as destination:
    destination.write(html)

print(html)
