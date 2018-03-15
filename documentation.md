---
author: Tillo Bosshart
title: SAD
subtitle: Simply Awesome Documents
thanks: Thanks go out to John MacFarlane for pandoc
...

# Idea

Wouldn't it cool to use the power of \XeLaTeX{} with the ease of writing a Markdown file and some json?

Pandoc makes at least the first part. So hacking together some Python to take part of the second was just a logical consequence.

# How to set Up
	
## settings.json

There is a global settings.json, which goes into the same directory as the main.py.

## user_settings.json

There can be a user_settings.json in the working directory, which overwrites the global settings.

## settings.json example:

~~~~~~~~~json
{
	"replacements":{
		"foo":"bar",
	},
	"variables":{
		"mainfont": "Linux Libertine O",
		"sansfont": "Linux Biolinum"
	},
	"extensions":["yaml_metadata_block"],
	"options":{
		"numbered_headings":"True",
		"toc":"True"
	},
	"loglevel":"DEBUG",
	"files": [
		{
			"in_file":"README.md",
			"out_file":"out.pdf",
			"template":"templates/shortcuts.tex"
		}
	]
}
~~~~~~~~~~~~~~

In detail:

### replacements:

*foo* gets replaced by *bar* before calling pandoc, thats how I made the keyboard symbols using a set of replacements and Biolinum Keyboard font.

### variables: 

Variables for Pandoc PDF generation using  \XeLaTeX{}: 

papersize
:	paper size, e.g. *letter*, *a4*

fontsizefont
:	size for body text (e.g. *10pt*, *12pt*)

documentclass
:	document class, e.g. *article*, *report*, *book*, *memoir*

classoption
:	option for document class, e.g. *oneside*; may be repeated for multiple options

geometry
:	option for geometry package, e.g. *margin=1in*; may be repeated for multiple options

margin-left, margin-right, margin-top, margin-bottom
:	sets margins, if geometry is not used (otherwise geometry overrides these)

linestretch
:	adjusts line spacing using the setspace package, e.g. 1.25, 1.5

mainfont, sansfont, monofont, mathfont, CJKmainfont
:	font families for use with xelatex or lualatex: take the name of any system font, using the fontspec package. Note that if CJKmainfont is used, the xecjk package must be available.

mainfontoptions, sansfontoptions, monofontoptions, mathfontoptions, CJKoptions
:	options to use with mainfont, sansfont, monofont, mathfont, CJKmainfont in xelatex and lualatex. Allow for any choices available through fontspec, such as the OpenType features *Numbers=OldStyle,Numbers=Proportional*. May be repeated for multiple options.

microtypeoptions
:	options to pass to the microtype package

colorlinks
:	add color to link text; automatically enabled if any of *linkcolor*, *citecolor*, *urlcolor*, or *toccolor* are set

linkcolor, citecolor, urlcolor, toccolor
:	color for internal links, citation links, external links, and links in table of contents: uses options allowed by xcolor, including the dvipsnames, svgnames, and x11names lists

links-as-notes
:	causes links to be printed as footnotes

indent
:	uses document class settings for indentation (the default LaTeX template otherwise removes indentation and adds space between paragraphs)

subparagraph
:	disables default behavior of LaTeX template that redefines (sub)paragraphs as sections, changing the appearance of nested headings in some classes

thanks
:	specifies contents of acknowledgments footnote after document title.

toc-depth
:	level of section to include in table of contents

secnumdepth
:	numbering depth for sections, if sections are numbered

bibliography
:	bibliography to use for resolving references

biblio-style
:	bibliography style, when used with --natbib and --biblatex.

biblio-title
:	bibliography title, when used with --natbib and --biblatex.

biblatexoptions
:	list of options for biblatex.

natbiboptions
:	list of options for natbib.

pagestyle
:	An option for LaTeX’s *pagestyle*. The default article class supports *plain* (default), *empty*, and *headings*; headings puts section titles in the header.

**Warning:** I didn't test all the variables, the way the script works is just giving them to Pandoc, so you probably better try it before.

### extensions

Adds Pandoc extensions to the call to Pandoc, by default *yaml_metadata_block* is set.

### options

The part of the default *settings.json*, just to show you the possible options

~~~~~json
	{
		"numbered_headings":"True",
		"toc":"False",
		"lof":"False",
		"lot":"False",
		"verbose":"False"
	},
~~~~~~~


### loglevel

Sets the log level, possible values are *CRITICAL*,*ERROR*,*WARNING*,*INFO*,*DEBUG*. Default is *INFO*

### files

Sets input file, outputfile and template(optional).


[[crtl]]+[[alt]]

[[T]][[I]][[L]][[L]][[0]]
