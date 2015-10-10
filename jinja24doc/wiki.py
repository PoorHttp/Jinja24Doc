
from jinja2 import Undefined
from inspect import stack

import re
import os
import sys

if sys.version_info[0] == 2:
    import __builtin__ as builtins
    from io import open
else:
    import builtins

from apidoc import linked_api, G
from misc import uni, usage

_python_keywords = (
                'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
                'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
                'if', 'import', 'lambda', 'nonlocal', 'pass', 'raise', 'return',
                'try', 'while', 'with', 'yield', 'print')   # print is keyword in rst...
_operators      = ('in', 'is', 'and', 'or', 'not')
_builtin        = tuple(i for i in dir(builtins) if i[0] != '_')

_jinja_keywords = [
                '#}', '%}', 'Trueset', 'as', 'block', 'call', 'context', 'elif',
                'else', 'endblock', 'endcall', 'endfilter', 'endfor', 'endif',
                'endmacro', 'endraw', 'extends', 'filter', 'for', 'from', 'if',
                'ignore', 'import', 'in', 'include', 'is', 'macro', 'missing',
                'not', 'raw', 'recursive', 'set', 'scoped', 'with', '{#', '{%',
                '{{', '}}']

re_lt       = re.compile(r"<")
re_gt       = re.compile(r">")
re_amp      = re.compile(r"&(?!amp;)")

# TODO: not work on multi type on same line :(
re_bold     = re.compile(r"\*(.+)\*")                       # * bold *
re_italic   = re.compile(r"/(.+)/")                         # / italic /
re_code     = re.compile(r"{(.+)}", re.S)                   # { code }

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

re_preauto  = re.compile(r"\n\s*\n( {4}.*?)(\n?)((\n\S)|$)", re.S)  # <pre>
re_notpre   = re.compile(r'(.*?)((<pre class="\w*">.*?</pre>)|$)', re.S) # 3 groups !
#        r"(^.*?<pre>)|(</pre>.*?<pre>)|(</pre>.*?$)|(^.*?$)", re.S)
re_param    = re.compile(r"(^|\n) {4}(\S*\s*)")

re_source   = re.compile(r'<pre class="(\w*)">(.*?)</pre>', re.S)

re_python   = re.compile(r"(\bdef \w+\b|\bclass \w+\b|\b\w+\b|\"[^\"]*\"|'[^\']*'|#.*|@[\w\.]+)")
re_jinja    = re.compile(r"(\b\w+\b|{{|}}|{%|%}|\".*\"|'[^\']*'|{#.*#})")
re_ini      = re.compile(r"(\n\s*\w+\b|\n\s*\[.*\]|#.*)", re.M)

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

    tmp = re_italic.sub(r"<i>\1</i>", tmp)
    tmp = re_bold.sub(r"<b>\1</b>", tmp)
    tmp = re_code.sub(r"<code>\1</code>", tmp)
    tmp = re_header4.sub(r"<h4>\1</h4>", tmp)
    tmp = re_header3.sub(r"<h3>\1</h3>", tmp)
    tmp = re_header2.sub(r"<h2>\1</h2>", tmp)
    tmp = re_param.sub(r'<br>\1<code class="param">\2</code>', tmp)
    return re_nlnl.sub(r'<br><br>\n\n', tmp)+groups[1]



def _python(obj):
    """ Highlight python syntax on Match object with one group """
    tmp = obj.group()
    if tmp[0] in ('"','\'','#'):
        return "<i>%s</i>" % tmp
    if tmp[0] in ('0','1','2','3','4','5','6','7','8','9'):
        return "<u>%s</u>" % tmp
    if tmp[0] == '@':
        return "<var>%s</var>" % tmp
    if tmp[:4] == "def ":
        return "<b>def</b> <em>%s</em>" % tmp[4:]
    if tmp[:6] == "class ":
        return "<b>class</b> <em>%s</em>" % tmp[6:]
    if tmp in _python_keywords:
        return "<b>%s</b>" % tmp
    if tmp in _operators:
        return "<tt>%s</tt>" % tmp
    if tmp in _builtin:
        return "<kbd>%s</kbd>" % tmp
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

def wiki(doc, name = '__doc__', section_level = 2):    # jinja function
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
    #sys.stdout.write("doc: %s\n" % doc)
    doc = re_notpre.sub(_not_in_pre, doc)

    # highlighting in pre tags
    doc = re_source.sub(_code, doc)

    # links
    doc = re_link.sub(r'<a href="\1">\1</a>', doc)

    doc = linked_api(doc)               # api keywords

    doc = re_pep3.sub(          # pep with 3 numbers
            r'<a href="http://www.python.org/dev/peps/pep-0\2/">\1\2</a>',doc)
    doc = re_pep4.sub(          # pep with 4 numbers
            r'<a href="http://www.python.org/dev/peps/pep-\2/">\1\2</a>', doc)
    doc = re_rfc.sub(           # rfc
            r'<a href="http://www.faqs.org/rfcs/rfc\2/">\1\2</a>', doc)

    return _nlstrip(doc)


def load_text(textfile):    # deprecated alias for load_wiki
    sys.stderr.write("[W] Using deprecated function load_text in\n")
    for s in stack()[1:]:
        sys.stderr.write("  File %s, line %s, in %s\n" % s[1:4])
        sys.stderr.write(s[4][0])
    sys.stderr.flush()
    return load_wiki(textfile)

def load_wiki(textfile, link = 'link', top = 'top', encoding = 'utf-8'):    # jinja function
    """
    Load file and create docs list of headers and texts.
        textfile - string, text file name (manual.txt)
        link - link label for headers. If is empty, link href will be hidden.
        top - top label for headers. If is empty, top href will be hidden.

        #!jinja
        {% set sections = load_wiki('file.txt', '', '') %}
        {% type, filename, _none_, text = sections[-1] %}
    """
    doc = []
    tmp = ''
    x_textfile = ''
    for path in G.paths:
        if os.access(path+'/'+textfile, os.R_OK):
            x_textfile = path+'/'+textfile
            break
    if not x_textfile:
        usage('Access denied to text file %s' % textfile)

    out = ''
    with open (x_textfile, 'r', encoding = encoding) as f:
        for line in f:
            match = re_section4.search(line) or re_section3.search(line) or \
                    re_section2.search(line) or re_section1.search(line)
            if match:
                if tmp:                     # add block before header to doc
                    #doc.append(('text', '', None, wiki(uni(tmp))))
                    out += wiki(uni(tmp))
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

                id = name.lower().replace(' ', '-')
                doc.append((type, uni(name), id, ''))
                out += '<%s>%s' % (type, name)
                if type != 'h1' and (link or top):
                    out += '<span class="links">'
                    if link:
                        out += '<a href="#%s">%s</a>' % (id, link)
                        out += ' | ' if link and top else ''
                        out += '<a href="#">%s</a>' % top
                    out += '</span>'
                out += '</%s>\n' % type
            else:
                tmp += line
        #endfor
    out += wiki(uni(tmp))
    #doc.append(('text', '', None, wiki(uni(tmp))))
    doc.append(('text', textfile, None, out))
    return doc


def load_source(srcfile, code = 'python', encoding = 'utf-8'):
    """
    Load source and format them as code

        #!jinja
        {{ load_source('example.py') }}
        {{ load_source('example.ini', 'ini') }}
    """
    x_srcfile = ''
    for path in G.paths:
        if os.access(path+'/'+srcfile, os.R_OK):
            x_srcfile = path+'/'+srcfile
            break
    if not x_srcfile:
        usage('Access denied to text file %s' % srcfile)

    doc = ''
    with open (x_srcfile, 'r', encoding = encoding) as f:
        class Obj:
            def groups(self):
                doc = uni(f.read())
                doc = re_amp.sub(r"&amp;", doc)
                doc = re_gt.sub(r"&gt;", doc)
                doc = re_lt.sub(r"&lt;", doc)
                return (code, doc)

        # highlighting in pre tags
        doc = _code(Obj())

        # links
        doc = re_link.sub(r'<a href="\1">\1</a>', doc)

        doc = linked_api(doc)       # api keywords

        doc = re_pep3.sub(          # pep with 3 numbers
                r'<a href="http://www.python.org/dev/peps/pep-0\2/">\1\2</a>',doc)
        doc = re_pep4.sub(          # pep with 4 numbers
                r'<a href="http://www.python.org/dev/peps/pep-\2/">\1\2</a>', doc)
        doc = re_rfc.sub(           # rfc
                r'<a href="http://www.faqs.org/rfcs/rfc\2/">\1\2</a>', doc)
    return doc
