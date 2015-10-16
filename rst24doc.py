#!/usr/bin/python
"""Jinja24Doc rst2doc tool"""

from sys import path as python_path, version_info, stderr
from os import path
from traceback import format_exc

from jinja24doc.apidoc import G
from jinja24doc.main import generate, parse_args
from jinja24doc.misc import usage

if version_info[0] == 2:
    from io import open


args = parse_args(__doc__)
try:
    source = args.source
    stylesheets = args.stylesheet.split(',')

    if args.verbose:
        stderr.write("rst24doc proccessing %s " % source)
        if args.output:
            stderr.write("-> %s\n" % args.output)
        else:
            stderr.write("...\n")
    # endif verbose

    if args.embed_stylesheet:
        embed_stylesheet = ''
        for stylesheet in stylesheets:
            try:
                with open(stylesheet, 'rt', encoding=args.encoding) as css:
                    embed_stylesheet += '<style source="%s">\n      ' % \
                                        stylesheet
                    embed_stylesheet += css.read().replace('\n', "\n      ")
                    embed_stylesheet += "</style>\n"
            except BaseException as e:
                usage("Can't read stylesheet %s:\n\t%s" % (stylesheet, e))

    kwargs = {
        'link': args.link,
        'top': args.top,
        'encoding': args.encoding,
        'system_message': args.system_message
    }
    if args.embed_stylesheet:
        kwargs['embed_stylesheet'] = embed_stylesheet
    else:
        kwargs['stylesheets'] = stylesheets

    file_name, ext = path.splitext(path.basename(source))

    if path.isdir(source) or ext == '.py':
        python_path.insert(0, path.abspath(path.dirname(source)))
        kwargs.update({'title': file_name,
                       'module': file_name})
        data = generate("module.html", G.paths, **kwargs)
    elif ext in ('.rst', '.txt'):
        G.paths.insert(0, path.abspath(path.dirname(source)))
        kwargs['source'] = path.basename(source)
        data = generate("text.html", G.paths, ** kwargs)
    else:
        usage('Unsuported source %s' % source)

    if args.output:
        with open(args.output, 'w+', encoding=args.encoding) as o:
            o.write(data)
    else:
        print(data)
except SystemExit as e:
    pass
except BaseException as e:
    usage('Error while proccessing %s' % e)
finally:
    if args.traceback:
        stderr.write(format_exc())
