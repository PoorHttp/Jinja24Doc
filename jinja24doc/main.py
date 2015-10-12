
from jinja2 import Environment, FileSystemLoader
from traceback import format_exception

import sys
import os

from sys import path as python_path
from os import path

from jinja24doc.misc import usage
from jinja24doc.apidoc import G
from jinja24doc.wiki import wiki, load_wiki, load_text, load_source
from jinja24doc.rst import rst, load_rst
from jinja24doc.apidoc import load_module, keywords



def local_name(name):
    """
    Returns striped name from its parent (module or class).

        #!jinja
        {{ local_name('MyClass.__init__') }} {# put __init__ to document #}
    """
    dot = name.rfind('.')
    return name[dot+1:]


def property_info(info, delimiter = ' | '):
    """
    Returns property info from tupple, where there is flags if property is
    writable,  readable and deletable.

        #!jinja
        {{ property_info(info) }}       {# return someone like this: WRITE | READ | DELETE #}
    """
    rv = []
    if info[0]: rv.append('READ')
    if info[1]: rv.append('WRITE')
    if info[2]: rv.append('DELETE')
    return delimiter.join(rv)


def log(message):
    """
    Write message to stderr.

        #!jinja
        {% do log('some debug message') %}
    """
    sys.stderr.write("%s\n" % message)


def _truncate(string, length = 255, killwords = True, end='...'):
    """ Only True yet """
    if len(string) > length:
        return string[:length] + end
    return string


def _generate(fname, path):
    env = Environment(loader=FileSystemLoader(path),
                      trim_blocks = True,
                      extensions=['jinja2.ext.do'],
                      lstrip_blocks = True)     # add in 2.7
    env.globals['load_module']  = load_module
    env.globals['wiki']     = wiki
    env.globals['rst']      = rst
    env.globals['keywords'] = keywords
    env.globals['load_wiki']    = load_wiki
    env.globals['load_text']    = load_text
    env.globals['load_rst']     = load_rst
    env.globals['load_source']  = load_source
    env.globals['local_name']   = local_name
    env.globals['property_info']= property_info
    env.globals['log']          = log

    # jinja2 compatibility with old versions
    env.globals['length']    = len
    env.globals['truncate']  = _truncate

    temp = env.get_template(fname)
    return temp.render(filename = fname)


def main():
    if len(sys.argv) < 2:
        usage('Not enough arguments')
    verbose = False

    if sys.argv[1] == '-v':         # verbose mode is set on
        if len(sys.argv) < 3:
            usage('Not enough arguments')
        verbose = True

        fname = sys.argv[2]

        if len(sys.argv) > 3:
            G.paths = sys.argv[3].split(':') + G.paths
    else:                           # not verbose option
        fname = sys.argv[1]

        if len(sys.argv) > 2:
            G.paths = sys.argv[2].split(':') + G.paths

    G.paths.insert(0, '.')

    x_fname = None
    for path in G.paths:
        if os.access(path+'/'+fname, os.R_OK):
            x_fname = path+'/'+fname
            if verbose:
                sys.stderr.write('jinja24doc processing %s ...\n' % x_fname)
            break

    if not x_fname:
        usage('Access denied to template %s' % fname)

    sys.path.insert(0, os.getcwd())
    try:
        data = _generate(fname, G.paths)
        if not isinstance(data, str):
            data = data.encode('utf-8')
        sys.stdout.write(data)
    except SystemExit as e:
        sys.exit(e.code)
    except:
        traceback = format_exception(sys.exc_type,
                                 sys.exc_value,
                                 sys.exc_traceback)
        traceback = ''.join(traceback)
        usage("Exception: %s" % traceback)
