"""Frontend command functions.

Module containts some funtcions which are run by command tools.
"""
from traceback import format_exc
from argparse import ArgumentParser
from sys import path as python_path, version_info, stderr
from os import path

if version_info[0] == 2:
    from io import open         # python3x compatible open

import os

from jinja24doc import __version__
from jinja24doc.context import Context


def build_parser(description):
    """Create ArgumentParser instance with all suported options."""
    parser = ArgumentParser(
        description=description,
        usage="%(prog)s [options] SOURCE [PATH[:PATH]]")

    parser.add_argument(
        "source", type=str,
        help="python module or reStructured text file",
        metavar="SOURCE")
    parser.add_argument(
        "path", default="", type=str, nargs='?', metavar="PATH[:PATH]",
        help="template paths separated by colon")
    parser.add_argument(
        "-O", "--output", type=str, metavar="FILE",
        help="write html to output file insead of stdout")
    parser.add_argument(
        "--encoding", default="utf-8", type=str, metavar="STRING",
        help="write html to output file insead of stdout")
    parser.add_argument(
        "--stylesheet",  default="style.css", type=str, metavar="FILE[,FILE]",
        help="stylesheet file name (default style.css)")
    parser.add_argument(
        "--embed-stylesheet", action="store_true",
        help="embed the stylesheet(s) in the output HTML file "
             "(default: False)")
    parser.add_argument(
        "--system-message", action="store_true",
        help="output system messages to output html (default: False)")
    link_group = parser.add_mutually_exclusive_group()
    link_group.add_argument(
        "--link", default="link", type=str, metavar="STRING",
        help="the `link' string (default: `link')")
    link_group.add_argument(
        "--no-link", action="store_const", const='', dest='link',
        help="don't create the `link' link for sections.")
    top_group = parser.add_mutually_exclusive_group()
    top_group.add_argument(
        "--top", default="top", type=str, metavar="STRING",
        help="the `top' string (default: `top')")
    top_group.add_argument(
        "--no-top", action="store_const", const='', dest='top',
        help="don't create the `top' link for sections.")
    parser.add_argument(
        "--traceback", action="store_true",
        help="Enable Python tracebacks.")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="verbose mode")
    parser.add_argument(
        '--version', action='version', version='%%(prog)s %s' % __version__)
    return parser


def verbose(args, parser):
    """Print info message to stderr when verbose option is set."""
    if args.verbose:
        stderr.write("%s proccessing %s " % (parser.prog, args.source))
        if args.output:
            stderr.write("-> %s\n" % args.output)
        else:
            stderr.write("...\n")
    # endif verbose


def embed_stylesheet(args, stylesheets):
    """Return stylesheets content readed from stylesheets."""
    embed_stylesheet = ''
    for stylesheet in stylesheets:
        try:
            with open(stylesheet, 'rt', encoding=args.encoding) as css:
                embed_stylesheet += '<style source="%s">\n      ' % \
                                    stylesheet
                embed_stylesheet += css.read().replace('\n', "\n      ")
                embed_stylesheet += "</style>\n"
        except BaseException as e:
            raise SystemExit("Can't read stylesheet %s:\n\t%s" %
                             (stylesheet, e))
    return embed_stylesheet
# enddef


def process(ctx, source, file_types, **kwargs):
    """Run Context.generate on right internal template dependend on file_types.
    """
    if source[-1] == '/':
            source = source[:-1]
    file_name, ext = path.splitext(path.basename(source))

    if path.isdir(source) or ext == '.py':
        python_path.insert(0, path.abspath(path.dirname(source)))
        kwargs.update({'title': file_name,
                       'module': file_name})
        output = ctx.generate("module.html", **kwargs)
    elif ext in (file_types):
        ctx.paths.insert(0, path.abspath(path.dirname(source)))
        kwargs['source'] = path.basename(source)
        output = ctx.generate("text.html", ** kwargs)
    else:
        raise SystemExit("Unsupport file type `%s'." % source)
    return output


def jinja_cmdline(description=''):
    """Function called by jinja24doc command tool."""
    parser = build_parser(description)
    args = parser.parse_args()
    try:
        ctx = Context(args.path, args.encoding)
        python_path.insert(0, os.getcwd())

        source = args.source
        # TODO: styles
        verbose(args, parser)

        kwargs = {
            'link': args.link,
            'top': args.top,
            'system_message': args.system_message,
            'encoding': args.encoding
        }

        output = ctx.generate(source, **kwargs)

        if args.output:
            with open(args.output, 'w+', encoding=args.encoding) as o:
                o.write(output)
        else:
            if not isinstance(output, str):
                output = output.encode('utf-8')
            print(output)
    except SystemExit as e:
        if args.traceback:
            stderr.write("%s\n" % args)
            stderr.write(format_exc())
        parser.error(e.message)
    except BaseException as e:
        if args.traceback:
            stderr.write("%s\n" % args)
            stderr.write(format_exc())
        parser.error('Error while proccessing %s' % e)
# enddef


def auto_cmdline(description='', formater='rst', file_types=['.txt']):
    """Function called by rst24doc and wiki24doc command tools."""
    parser = build_parser(description)
    args = parser.parse_args()
    try:
        ctx = Context(args.path, args.encoding)

        source = args.source
        stylesheets = args.stylesheet.split(',')
        verbose(args, parser)

        kwargs = {
            'link': args.link,
            'top': args.top,
            'system_message': args.system_message,
            'encoding': args.encoding,
            'formater': getattr(ctx, formater)
        }

        if args.embed_stylesheet:
            kwargs['embed_stylesheet'] = embed_stylesheet(args, stylesheets)
        else:
            kwargs['stylesheets'] = stylesheets

        output = process(ctx, source, file_types, **kwargs)

        if args.output:
            with open(args.output, 'w+', encoding=args.encoding) as o:
                o.write(output)
        else:
            if not isinstance(output, str):
                output = output.encode('utf-8')
            print(output)
    except SystemExit as e:
        if args.traceback:
            stderr.write("%s\n" % args)
            stderr.write(format_exc())
        parser.error(e.message)
    except BaseException as e:
        if args.traceback:
            stderr.write("%s\n" % args)
            stderr.write(format_exc())
        parser.error('Error while proccessing %s' % e)
# enddef
