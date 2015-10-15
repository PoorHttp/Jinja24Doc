#!/usr/bin/python
"""Jinja24Doc rst2doc tool"""

from sys import path as python_path, version_info
from os import path

from jinja24doc.apidoc import G
from jinja24doc.main import generate, parse_args

if version_info[0] == 2:
    from io import open


G.re_docs = None
G._api_url = ''
G._api_keywords = {}
G._modules = []

args = parse_args(__doc__)
source = args.source
print args

if source.endswith('py'):
    python_path.insert(0, path.abspath(path.dirname(source)))
    data = generate("module.html", G.paths,
                    title=path.basename(source)[:-3],
                    module=path.basename(source)[:-3],
                    stylesheets=args.stylesheet.split(','),
                    link=args.link, top=args.top,
                    encoding=args.encoding)
elif source.endswith('rst'):
    G.paths.insert(0, path.abspath(path.dirname(source)))
    data = generate("text.html", G.paths,
                    source=path.basename(source),
                    stylesheets=args.stylesheet.split(','),
                    link=args.link, top=args.top,
                    encoding=args.encoding)

if args.output:
    with open(args.output, 'w+', encoding=args.encoding) as o:
        o.write(data)
else:
    print(data)
