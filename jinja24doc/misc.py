# -*- coding: utf-8 -*-
import sys

parser = None
encoding = 'utf-8'
unicode_exist = True

__version__ = "1.2.99"
__author__ = "Ondřej Tůma"
__date__ = "Oct 15 2015"

try:
    unicode()
except:
    unicode_exist = False


def uni(text):
    """ Function always return unicode or str in Python 3.x """
    if unicode_exist and isinstance(text, str):
        return text.decode(encoding)
    return text


def usage(err=None):
    if parser:
        if err:
            parser.error(err)
        else:
            parser.print_usage(sys.stderr)
            parser.exit()

    sys.stderr.write("Usage: %s [-v] template [path]\n" % sys.argv[0])
    sys.stderr.write("    -v            verbose mode\n")
    sys.stderr.write("    template      jinja2 template\n")
    sys.stderr.write("    path          list of path separates by colon where "
                     "tempates are\n")
    sys.stderr.write("Error:\n    %s\n" % err)
    sys.exit(1)
