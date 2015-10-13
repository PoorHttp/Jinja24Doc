import sys

unicode_exist = True

try:
    unicode()
except:
    unicode_exist = False


def uni(text):
    """ Function always return unicode or str in Python 3.x """
    if unicode_exist and isinstance(text, str):
        return text.decode('utf-8')
    return text


def usage(err=None):
    sys.stderr.write("Usage: %s [-v] template [path]\n" % sys.argv[0])
    sys.stderr.write("    -v            verbose mode\n")
    sys.stderr.write("    template      jinja2 template\n")
    sys.stderr.write("    path          list of path separates by colon where "
                     "tempates are\n")
    sys.stderr.write("Error:\n    %s\n" % err)
    sys.exit(1)
