# -*- coding: utf-8 -*-
from sys import stderr

parser = None
encoding = 'utf-8'
unicode_exist = True

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
    if err:
        parser.error(err)
    else:
        parser.print_usage(stderr)
        parser.exit()


def log(message):
    """
    Write message to stderr.

        #!jinja
        {% do log('some debug message') %}
    """
    stderr.write("%s\n" % message)
