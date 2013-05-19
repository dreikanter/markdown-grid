# Markdown Grid Extension

This is [Markdown](http://daringfireball.net/projects/markdown/) extension
for grid building. It provides minimal and straightforward syntax to create
multicolumn text layouts. By default the extension generates [Twitter
Bootstrap](http://twitter.github.com/bootstrap/) compatible HTML code but
it is intended to be template-agnostic. It could be configured to use any other
HTML/CSS framework (e.g. [Skeleton](http://getskeleton.com)) or custom design.


## The Syntax

Markdown syntax extension is pretty simple. Page source example below defines
a threee-column page fragment:

```markdown
-- row 5, 2, 5 --
First column contains couple of paragraphs. Lorem ipsum dolor sit amet,
consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea commodo consequat.
---
Some images in the middle column:
![One](image-1.png)
![Two](image-2.png)
---
And some **more** text in the _third_ column. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

[Excepteur](http://excepteur.org ) sint occaecat cupidatat non proident, sunt
in culpa qui officia deserunt mollit anim id est laborum.
-- end --
```

Comma separated list of numbers after the `row` instruction is an optional
definition for columns width. This example uses 12-column Twitter Bootstrap
grid, so "5, 2, 5" corresponds to "41.5%, 17%, 41.5%" relatively to the total
page width.


## Processing

Grid extension uses two-stage processing flow:

1. On the first stage text preprocessor generates markdown-friendly tags based
on the original minimalistic syntax. Those tags are explicit instructions for
further layout building enclosed with HTML comments.
2. Second stage takes place after Markdown general processing. Extension
postprocessor replaces previously-inserted tags with actual HTML markup.

You will never see the intermediate page source processing result, but this
document use to be some kind of technical specification, so the details should
be described anyway.

Here is preprocessor output for the initial example:

```html
<!--mdtb:row,col4-->

First column contains couple of paragraphs. Lorem ipsum dolor sit amet,
consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea commodo consequat.

<!--mdtb:endcol,col4-->

Some images in the middle column:

![One](image-1.png)

![One](image-1.png)

<!--mdtb:endcol,col4-->

And some **more** text in the _third_ column. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

[Excepteur](http://excepteur.org) sint occaecat cupidatat non proident, sunt
in culpa qui officia deserunt mollit anim id est laborum.

<!--mdtb:endcol,endrow-->
```

The final result (as it was mentioned already it is based on Twitter
Bootstrap):

```html
<div class="row">
	<div class="span5">
		<p>First column contains couple of paragraphs. Lorem ipsum dolor sit
		amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt
		ut labore et dolore magna aliqua.</p>
		<p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
		nisi ut aliquip ex ea commodo consequat.</p>
	</div>
	<div class="span2">
		<p>Some images in the middle column:</p>
		<p><img alt="One" src="image-1.png" /></p>
		<p><img alt="One" src="image-1.png" /></p>
	</div>
	<div class="span5">
		<p>And some <strong>more</strong> text in the <em>third</em> column.
		Duis aute irure dolor in reprehenderit in voluptate velit esse cillum
		dolore eu fugiat nulla pariatur.</p>
		<p><a href="http://excepteur.org">Excepteur</a> sint occaecat
		cupidatat non proident, sunt in culpa qui officia deserunt mollit
		anim id est laborum.</p>
	</div>
</div>
```

## Installation

A command to install markdown-grid:

	pip install -e git+git://github.com/dreikanter/markdown-grid#egg=mdx_grid

Including markdown-grid to a package:

	setup(
	    name='example',
	    ...
	    install_requires=[
	        'markdown',
	        'mdx_grid',
	        ...
	    ],
	    dependency_links=[
	        'https://github.com/dreikanter/markdown-grid/tarball/master#egg=mdx_grid'
	    ],
	)

