#!/usr/bin/python
"""
    Jinja24doc is lightweight documentation generator for python modules with
    jinja2 templates. It is part of *Poor Http* group tools (WSGI connector,
    WSGI/HTTP Server and mod_python connector). It could load modules and gets
    documentation for its items. No configuration is needed, only jinja2
    templates. Your or from jinja2doc package.
"""

__author__  = "Ondrej Tuma (McBig) <mcbig@zeropage.cz>"
__date__    = "21 August 2014"
__version__ = "1.2.0"

from jinja2 import Environment, FileSystemLoader, Undefined
from traceback import format_exception
from inspect import getargspec, getdoc, getmembers, getsource, formatargspec, \
        isfunction, isroutine, ismethod, isclass, ismodule, isbuiltin, \
        ismethoddescriptor, isgetsetdescriptor
from operator import itemgetter

import sys, os, re

_unicode_exist = True
try:
    unicode()
except:
    _unicode_exist = False


_python_keywords = [
                'False', 'None', 'True', 'and', 'as', 'assert', 'break',
                'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
                'finally', 'for', 'from', 'global', 'if', 'import', 'in',
                'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
                'return', 'try', 'while', 'with', 'yield']

_jinja_keywords = [
                '#}', '%}', 'Trueset', 'as', 'block', 'call', 'context', 'elif',
                'else', 'endblock', 'endcall', 'endfilter', 'endfor', 'endif',
                'endmacro', 'endraw', 'extends', 'filter', 'for', 'from', 'if',
                'ignore', 'import', 'in', 'include', 'is', 'macro', 'missing',
                'not', 'raw', 'recursive', 'set', 'scoped', 'with', '{#', '{%',
                '{{', '}}']


_ordering   = { 'module'    : (0,0),
                'submodule' : (1,0),
                'dependence': (1,1),
                'class'     : (2,0),
                'property'  : (2,1),
                'descriptor': (2,2),
                'method'    : (2,3),
                'staticmethod' : (2,4),
                'function'  : (3,0),
                'variable'  : (4,0)}

re_lt       = re.compile(r"<")
re_gt       = re.compile(r">")
re_amp      = re.compile(r"&(?!amp;)")
# TODO: not work on multi type on same line :(
re_bold     = re.compile(r"\*(.*?)\*")                              # * bold *
re_italic   = re.compile(r"\s/(.*?)/\b")                            # / italic /
re_code     = re.compile(r"{(.*?)}", re.S)                          # { code }

re_section1 = re.compile(r"^(={1})([^=]+)(={1}\s*)")
re_section2 = re.compile(r"^(={2})(.*?)(={2}\s*)")
re_section3 = re.compile(r"^(={3})(.*?)(={3}\s*)")
re_section4 = re.compile(r"^(={4})(.*?)(={4}\s*)")

re_header2  = re.compile(r"==(.*?)==")                              # = head3 =
re_header3  = re.compile(r"===(.*?)===")                            # = head3 =
re_header4  = re.compile(r"====(.*?)====")                          # = head4 =
re_nlnl     = re.compile(r"(\n\s*\n)")                              # <br><br>

re_pep3     = re.compile(r"\b(PEP )([0-9]{3})\b")               # pep link
re_pep4     = re.compile(r"\b(PEP )([0-9]{4})\b")               # pep link
re_rfc      = re.compile(r"\b(RFC )([0-9]+)\b")                 # rfc link
re_link     = re.compile(r"((http|https|git|ftp)://[^\s<>]*)", re.I)

re_notlink  = re.compile(r"(.*?)((<a .*?</a>)|$)", re.S)

re_preauto  = re.compile(r"\n\s*\n( {4}.*?)(\n?)((\n\S)|$)", re.S)  # <pre>
re_notpre   = re.compile(r'(.*?)((<pre class="\w*">.*?</pre>)|$)', re.S) # 3 groups !
#        r"(^.*?<pre>)|(</pre>.*?<pre>)|(</pre>.*?$)|(^.*?$)", re.S)
re_param    = re.compile(r"(^|\n) {4}(\S*\s*)")

re_source   = re.compile(r'<pre class="(\w*)">(.*?)</pre>', re.S)

re_python   = re.compile(r"(\bdef \w+\b|\bclass \w+\b|\b\w+\b|\"[^\"]*\"|'[^\']*'|#.*|@[\w\.]+)")
re_jinja    = re.compile(r"(\b\w+\b|{{|}}|{%|%}|\".*\"|'[^\']*'|{#.*#})")
re_ini      = re.compile(r"(\n\s*\w+\b|\n\s*\[.*\]|#.*)", re.M)

re_docs     = None

_api_url        = ''
_api_keywords   = {}
_modules        = []


class Fn:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

def _str(text):
    if _unicode_exist and isinstance(text, str):
        return text.decode('utf-8')
    return text

def _key_doc(a):
    o = _ordering[a[0]]
    return str(o[0])+a[1].replace('.',str(o[1]))


def load_module(module):                    # jinja function
    """
        get documentation of function, variables and classes from module

            #!jinja
            {% set api = load_module('module') %}
            {% for type, name, args, doc = api[0] %}
                ...
    """
    try:
        ml = module.split('.')
        module = __import__(module)
        for it in ml[1:]:                   # if module is submodule
            module = module.__getattribute__(it)
    except Exception as e:
        sys.stderr.write(repr(e)+'\n')
        return []

    _file = module.__file__ if '__file__' in module.__dict__ else module.__name__
    if _file in _modules:
        return []
    else:
        _modules.append(_file)

    try:
        source = getsource(module)
    except:
        source = ''

    dependences = set()
    doc = []
    modinfo = {'author': None, 'date': None, 'version': None}
    
    for name, item in getmembers(module):
        if isclass(item):                       # module classes
            if module.__name__ != item.__module__:
                continue
            doc.append(('class',                                        # type
                        _str(item.__name__),                            # name
                        None,                                           # args
                        _str(getdoc(item) or '')))                      # doc

            for nm, it in getmembers(item):     # class members
                if ismethod(it) or isfunction(it) or ismethoddescriptor(it) or isgetsetdescriptor(it):
                    try:
                        mtype = 'descriptor'
                        if sys.version_info[0] > 2: # python 3.x
                            if isfunction(it):
                                mtype = 'method'
                            elif isinstance(it, staticmethod):
                                mtype = 'staticmethod'
                        else:                       # python 2.x
                            if ismethod(it):
                                mtype = 'method'
                            elif isfunction(it):
                                mtype = 'staticmethod'

                        if isinstance(it, staticmethod):    # python 3.x
                            it = it.__func__
                        
                        args, vargs, kwords, defaults = getargspec(it)
                        if defaults:
                            ndefaults = []                  # transport functions to their names
                            for d in defaults:
                                if isfunction(d):
                                    ndefaults.append(Fn(".".join((d.__module__, d.__name__))))
                                elif ismethod(d):
                                    ndefaults.append(Fn(".".join((d.__objclass__, d.__name__))))
                                else:
                                    ndefaults.append(d)
                            defaults = ndefaults

                        doc.append((mtype,                                  # type
                            _str(item.__name__) + '.' + _str(it.__name__),  # name
                            formatargspec(args, vargs, kwords, defaults),   # args
                            getdoc(it) or ''))                              # doc
                    except:
                        pass

                elif isinstance(it, property):
                    doc.append(('property',                                 # type
                            _str(item.__name__) + '.' + \
                                        _str(nm),                           # name
                            (bool(it.fget), bool(it.fset), bool(it.fdel)),  # property info
                            getdoc(it) or ''))                              # doc
                # elif isbuiltin(it):    <- __new__, __subclasshook__
                else:
                    pass

        elif isfunction(item) or isroutine(item):           # module function
            if module.__name__ != item.__module__:
                dependences.add(item.__module__)            # append to dependences
                continue

            if not isbuiltin(item):
                args, vargs, kwords, defaults = getargspec(item)
                if defaults:
                    ndefaults = []                  # transport functions to their names
                    for d in defaults:
                        if isfunction(d):
                            ndefaults.append(Fn(".".join((d.__module__, d.__name__))))
                        elif ismethod(d):
                            ndefaults.append(Fn(".".join((d.__objclass__, d.__name__))))
                        else:
                            ndefaults.append(d)
                    defaults = ndefaults

                doc.append(('function',                                 # type
                        name,                                           # name
                        formatargspec(args, vargs, kwords, defaults),   # args
                        getdoc(item) or ''))                            # doc
            else:
                bdoc = getdoc(item) or ''
                if bdoc.find(name) == 0:
                    eol = bdoc.find('\n')
                    args = bdoc[len(name):eol]
                    bdoc = bdoc[eol:].strip()
                else:
                    args = ''

                doc.append(('function',                                 # type
                        name,                                           # name
                        args,                                           # args
                        bdoc))                                          # doc

        elif ismodule(item):
            doc.append(('submodule',name, None, ''))
        elif isinstance(item, re._pattern_type):
            if name[0:2] == '__' or not re.search("\n%s\s*=" % name, source):
                continue
            match = re.search("\n#\s*([^\n]*)\n%s\s*=" % name, source)
            comment = match.groups()[0] if match else ''
            doc.append(('variable',                                     # type
                        name,                                           # name
                        "(%s, %s)" % (item.pattern, item.flags),        # value
                        comment))                                       # doc
        else:
            if name[0:2] == '__' or not re.search("\n%s\s*=" % name, source):
                if name in ('__author__', '__date__', '__version__'):
                    modinfo[name.strip('_')] = repr(item)
                continue
            # get last previous comment start with hash char (#)
            match = re.search("\n#\s*([^\n]*)\n%s\s*=" % name, source)
            comment = match.groups()[0] if match else ''
            doc.append(('variable',                                     # type
                        name,                                           # name
                        repr(item),                                     # value
                        comment))                                       # doc
    #endfor

    doc.append(('module',
                module.__name__,
                (modinfo['author'], modinfo['date'], modinfo['version']),
                getdoc(module) or '' ))

    for name in dependences:
        doc.append(('dependence',name, None, ''))

    return sorted(doc, key = _key_doc)


def keywords(api, api_url = "",                 # jinja function
            types = ('module', 'class', 'method', 'staticmethod', 'descriptor',
                     'property', 'variable','function', 'h1', 'h2', 'h3')):
    """ Fill internal api_url variable from names of modules, classes, functions,
        methods, variables or h1, h2 and h3 sections. With this, wiki can create
        links to this functions  or classes.

            #!jinja
            {% set api = load_module('module') %}

            {# create api rexex for from module where api will be on module_api.html #}
            {% do keywords(api, 'module_api.html') %}

            {# create api rexex for from module where api will be on same page #}
            {% do keywords(api) %}

            {# another way how to call keywords function without do keyword #}
            {{ keywords(api) }}      {# keywords function return empty string #}

        Nice to have: there could be nice, if will be arguments in title, so
        mouseover event show some little detail of functions, methods or
        variables.
    """
    global re_docs
    global _api_url
    global _api_keywords

    api = sorted(api, key = itemgetter(1), reverse=True)
    # TODO: dict for mapping names to parametres (for title in href)

    re_docs = re.compile(r"(\b)(%s)(\b)" % \
                '|'.join((name.replace('.','\.') for type, name, args, doc in api if type in types )))
    _api_url = api_url

    _api_keywords = dict((name, (args if type != 'module' else None) or type) for type, name, args, doc in api)

    return ''


def _not_in_pre(obj):
    """ Do params blocks in code and put double enter if is in doc.
        This function gets Match object with more then 1 groups. First
        group must be founded as 'main' and second group must be next string.
            * return obj.groups()[0]+obj.groups()[1]
    """
    groups = obj.groups()
    if not groups[0]:           # r"(.*?)(('.*?')(\".*?\")|$)"
        return groups[1]

    tmp = groups[0]

    tmp = re_bold.sub(r"<b>\1</b>", tmp)
    tmp = re_italic.sub(r"<i>\1</i>", tmp)
    tmp = re_code.sub(r"<code>\1</code>", tmp)
    tmp = re_header4.sub(r"<h4>\1</h4>", tmp)
    tmp = re_header3.sub(r"<h3>\1</h3>", tmp)
    tmp = re_header2.sub(r"<h2>\1</h2>", tmp)
    tmp = re_param.sub(r'<br>\1<code class="param">\2</code>', tmp)
    return re_nlnl.sub(r'<br><br>\n\n', tmp)+groups[1]

def _keyword(obj):
    groups = obj.groups()
    key = groups[1]

    args = _api_keywords[key]

    tmp = '<a href="%s#%s" title="%s">%s</a>' % \
            (_api_url, key, args, key )
    return groups[0] + tmp + groups[2]


def _not_in_link(obj):
    groups = obj.groups()
    if not groups[0]:
        return groups[1]

    tmp = re_docs.sub(_keyword, groups[0])
    return tmp + groups[1]


def _python(obj):
    """ Highlight python syntax on Match object with one group """
    tmp = obj.group()
    if tmp[0] in ('"','\'','#'):
        return "<i>%s</i>" % tmp
    if tmp[0] in ('@','0','1','2','3','4','5','6','7','8','9'):
        return "<u>%s</u>" % tmp
    if tmp[:4] == "def ":
        return "<b>def</b> <em>%s</em>" % tmp[4:]
    if tmp[:6] == "class ":
        return "<b>class</b> <em>%s</em>" % tmp[6:]
    if tmp in _python_keywords:
        return "<b>%s</b>" % tmp
    return tmp


def _jinja(obj):
    """ Highlight python syntax on Match object with one group """
    tmp = obj.group()
    if tmp[0] in ('"','\''):
        return "<i>%s</i>" % tmp
    if tmp[0] in ('0','1','2','3','4','5','6','7','8','9'):
        return "<u>%s</u>" % tmp
    if tmp[0:2] in ('{#'):
        return "<i>%s</i>" % tmp
    if tmp in _jinja_keywords:
        return "<b>%s</b>" % tmp
    return tmp


def _ini(obj):
    """ Highlight ini syntax on Match object with one group """
    tmp = obj.group()
    if tmp[0] == '#':
        return "<i>%s</i>" % tmp
    if tmp[-1] == ']':
        return "\n<b>%s</b>" % tmp[1:]
    return "\n<u>%s</u>" % tmp[1:]          # variable


def _code(obj):
    """ Call highlight functions by class python, jinja or ini """
    tmp = obj.groups()
    if tmp[0] == 'python':
        source = re_python.sub(_python, tmp[1])
    elif tmp[0] == 'jinja':
        source = re_jinja.sub(_jinja, tmp[1])
    elif tmp[0] == 'ini':
        source = re_ini.sub(_ini, tmp[1])
    else:
        source = tmp[1]

    return '<pre class="%s">%s</pre>' % (tmp[0], source)


def _pre(obj):
    """ Create pre tag with specific code type. """
    groups = obj.groups()

    if groups[0][0:9] == '    #!ini':
        code = 'ini'
        source = groups[0][9:]
    elif groups[0][0:12] == '    #!python':
        code = 'python'
        source = groups[0][12:]
    elif groups[0][0:11] == '    #!jinja':
        code = 'jinja'
        source = groups[0][11:]
    elif groups[0][0:10] == '    #!text':
        code = 'text'
        source = groups[0][10:]
    else:                               # python is default
        code = 'python'
        source = groups[0]
    return '\n<pre class="%s">%s</pre>%s' % (code, source, groups[2])


def _nlstrip(s):
    s = s.strip()
    while s[:4] == '<br>':
        s = s[4:].strip()
    while s[-4:] == '<br>':
        s = s[:-4].strip()
    return s


def wiki(doc):    # jinja function
    """ Call some regular expressions on doc, and return it with html
        interpretation of wiki formating. If you want to create links to know
        api for your module, just call keywords function after gets full api
        documentation list.

            #!jinja
            {{ wiki(string) }}
            {{ wiki('= header 1 =') }}          {# <h1> header 1 </h1> #}
            {{ wiki('= header 2 =') }}          {# <h2> header 2 </h2> #}
            {{ wiki('= header 3 =') }}          {# <h3> header 3 </h3> #}
            {{ wiki('= header 4 =') }}          {# <h4> header 4 </h4> #}
            {{ wiki('* bold text *') }}         {# <b> bold text </b> #}
            {{ wiki('/ italic text /') }}       {# <i> iatlic text </i> #}
            {{ wiki('{ code text }') }}         {# <code> code text </code> #}

        Formated pre code type could be python (/default if not set/),
        jinja, ini or text. Text type stops highlighting. Code type
        must be on first line with hashbang prefix like in example:

            #!text
            #!python
            # simple python example
            from poorwsgi import *

            @app.route('/')                         # uri /
            def root(req):
                return 'Hello world %s' % 1234      # return text

        Looks that:

            #!python
            # simple python example
            from poorwsgi import *

            @app.route('/')                         # uri /
            def root(req):
                return 'Hello world %s' % 1234      # return text

        Parameters padding:

            #!text
            This is some text, which could be little bit long. Never mind if
            text is on next line.
                parameter - some text for parameter
                parameter - some text for parameter

        Looks that:

        This is some text, which could be little bit long. Never mind if
        text is on next line.
            parameter - some text for parameter
            parameter - some text for parameter

    """
    if isinstance(doc, Undefined):      # template error
        return doc

    doc = re_amp.sub(r"&amp;", doc)
    doc = re_gt.sub(r"&gt;", doc)
    doc = re_lt.sub(r"&lt;", doc)

    # main tags (pre, code and br)
    doc = re_preauto.sub(_pre, doc)
    doc = re_notpre.sub(_not_in_pre, doc)

    # highlighting in pre tags
    doc = re_source.sub(_code, doc)

    # links
    doc = re_link.sub(r'<a href="\1">\1</a>', doc)

    if not re_docs is None:     # api keywords
        doc = re_notlink.sub(_not_in_link, doc)

    doc = re_pep3.sub(          # pep with 3 numbers
            r'<a href="http://www.python.org/dev/peps/pep-0\2/">\1\2</a>',doc)
    doc = re_pep4.sub(          # pep with 4 numbers
            r'<a href="http://www.python.org/dev/peps/pep-\2/">\1\2</a>', doc)
    doc = re_rfc.sub(           # rfc
            r'<a href="http://www.faqs.org/rfcs/rfc\2/">\1\2</a>', doc)

    return _nlstrip(doc)


def load_text(textfile):    # jinja function
    """ Load file and create docs list of headers and texts.
        textfile - string, text file name (manual.txt)

            #!jinja
            {% set sections = load_text('file.txt') %}
            {% type, name, _none_, text = sections[0] %}
    """
    doc = []
    tmp = ''
    x_textfile = ''
    for path in paths:
        if os.access(path+'/'+textfile, os.R_OK):
            x_textfile = path+'/'+textfile
            break
    if not x_textfile:
        _usage('Access denied to text file %s' % textfile)

    with open (x_textfile, 'r') as f:
        for line in f:
            match = re_section4.search(line) or re_section3.search(line) or \
                    re_section2.search(line) or re_section1.search(line)
            if match:
                if tmp:                     # add block before header to doc
                    doc.append(('text', '', None, _str(tmp)))
                    tmp = ''
                name = match.groups()[1].strip()
                if match.re == re_section1:
                    type = 'h1'
                elif match.re == re_section2:
                    type = 'h2'
                elif match.re == re_section3:
                    type = 'h3'
                elif match.re == re_section4:
                    type = 'h4'
                else:
                    raise RuntimeError("No match regex")

                doc.append((type, _str(name), None, ''))
            else:
                tmp += line
        #endfor
    doc.append(('text', '', None, _str(tmp)))
    return doc


def load_source(srcfile, code = 'python'):
    """ Load source and format them as code

            #!jinja
            {{ load_source('example.py') }}
            {{ load_source('example.ini', 'ini') }}
    """
    x_srcfile = ''
    for path in paths:
        if os.access(path+'/'+srcfile, os.R_OK):
            x_srcfile = path+'/'+srcfile
            break
    if not x_srcfile:
        _usage('Access denied to text file %s' % srcfile)

    doc = ''
    with open (x_srcfile, 'r') as f:
        class Obj:
            def groups(self):
                doc = _str(f.read())
                doc = re_amp.sub(r"&amp;", doc)
                doc = re_gt.sub(r"&gt;", doc)
                doc = re_lt.sub(r"&lt;", doc)
                return (code, doc)

        # highlighting in pre tags
        doc = _code(Obj())

        # links
        doc = re_link.sub(r'<a href="\1">\1</a>', doc)

        if not re_docs is None:     # api keywords
            doc = re_notlink.sub(_not_in_link, doc)

        doc = re_pep3.sub(          # pep with 3 numbers
                r'<a href="http://www.python.org/dev/peps/pep-0\2/">\1\2</a>',doc)
        doc = re_pep4.sub(          # pep with 4 numbers
                r'<a href="http://www.python.org/dev/peps/pep-\2/">\1\2</a>', doc)
        doc = re_rfc.sub(           # rfc
                r'<a href="http://www.faqs.org/rfcs/rfc\2/">\1\2</a>', doc)
    return doc


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


def _usage(err = None):
    sys.stderr.write("Usage: %s [-v] template [path]\n" % sys.argv[0])
    sys.stderr.write("    -v            verbose mode\n")
    sys.stderr.write("    template      jinja2 template\n")
    sys.stderr.write("    path          list of path separates by colon where tempates are\n")
    sys.stderr.write("Error:\n    %s\n" % err)
    sys.exit(1)


def _generate(fname, path):
    env = Environment(loader=FileSystemLoader(path),
                      trim_blocks = True,
                      extensions=['jinja2.ext.do'])
                      #lstrip_blocks = True)     # add in 2.7
    env.globals['load_module']  = load_module
    env.globals['wiki']     = wiki
    env.globals['keywords'] = keywords
    env.globals['load_text']    = load_text
    env.globals['load_source']  = load_source
    env.globals['local_name']   = local_name
    env.globals['property_info']= property_info
    env.globals['log']          = log

    # jinja2 compatibility with old versions
    env.globals['length']    = len
    env.globals['truncate']  = _truncate

    temp = env.get_template(fname)
    return temp.render(filename = fname)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        _usage('Not enough arguments')
    verbose = False

    if sys.argv[1] == '-v':         # verbose mode is set on
        if len(sys.argv) < 3:
            _usage('Not enough arguments')
        verbose = True

        fname = sys.argv[2]

        if len(sys.argv) > 3:
            paths = sys.argv[3].split(':')
        else:
            paths = []
    else:                           # not verbose option
        fname = sys.argv[1]

        if len(sys.argv) > 2:
            paths = sys.argv[2].split(':')
        else:
            paths = []

    paths.insert(0, '.')

    x_fname = None
    for path in paths:
        if os.access(path+'/'+fname, os.R_OK):
            x_fname = path+'/'+fname
            if verbose:
                sys.stderr.write('jinja24doc processing %s ...\n' % x_fname)
            break

    if not x_fname:
        _usage('Access denied to template %s' % fname)

    sys.path.insert(0, os.getcwd())
    try:
        data = _generate(fname, paths)
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
        _usage("Exception: %s" % traceback)
