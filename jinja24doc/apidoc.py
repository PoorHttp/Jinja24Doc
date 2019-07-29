""" module api documentation reader """

from inspect import getargspec, getdoc, getmembers, getsource, formatargspec, \
    isfunction, isroutine, ismethod, isclass, ismodule, isbuiltin, \
    ismethoddescriptor, isgetsetdescriptor
from operator import itemgetter

import sys
import re

# from Python 3.7 re.Pattern type instead of re._pattern_type
try:
    from re import _pattern_type as Pattern
except ImportError:
    from re import Pattern


unicode_exist = True
try:
    unicode()
except:
    unicode_exist = False


ordering = {'module':       (0, 0),
            'submodule':    (1, 0),
            'dependence':   (1, 1),
            'class':        (2, 0),
            'property':     (2, 1),
            'descriptor':   (2, 2),
            'method':       (2, 3),
            'staticmethod': (2, 4),
            'function':     (3, 0),
            'variable':     (4, 0)}

re_notlink = re.compile(r"(.*?)((<a .*?</a>)|$)", re.S)

re_pep = re.compile(r"\bPEP ([0-9]{1,4})\b")            # pep link
re_rfc = re.compile(r"\b(RFC )([0-9]+)\b")              # rfc link


class Fn:
    """Support class for naming in module."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


def local_name(name):
    """Returns striped name from its parent (module or class).

    Typical use:

        #!jinja
        {{ local_name('MyClass.__init__') }} {# put __init__ to document #}
    """
    dot = name.rfind('.')
    return name[dot+1:]


def property_info(info, delimiter=' | '):
    """Returns property info from tupple.

    Input tuple must containts flags if property is writable, readable
    and deletable.

        #!jinja
        {# return someone like this: WRITE | READ | DELETE #}
        {{ property_info(info) }}
    """
    rv = []
    if info[0]:
        rv.append('READ')
    if info[1]:
        rv.append('WRITE')
    if info[2]:
        rv.append('DELETE')
    return delimiter.join(rv)


def key_doc(a):
    """Return string sortable item via ordering keys."""
    o = ordering[a[0]]
    return str(o[0])+a[1].replace('.', str(o[1]))


def _pep(obj):
    return '<a href="http://www.python.org/dev/peps/pep-{0:04}/">PEP {0}</a>'.\
        format(int(obj.groups()[0]))


def pep_rfc(doc):
    """Automatic create html links in doc from PEP and RFC notifications."""
    doc = re_pep.sub(_pep, doc)
    doc = re_rfc.sub(           # rfc
        r'<a href="http://www.faqs.org/rfcs/rfc\2/">\1\2</a>', doc)
    return doc


class ApiDoc(object):

    def __init__(self):
        self.re_docs = None
        self.api_url = ''
        self.api_keywords = {}
        self.paths = []
        self.modules = []
        self.encoding = 'utf-8'

    def __keyword(self, obj):
        groups = obj.groups()
        key = groups[1]
        args = self.api_keywords[key]
        tmp = '<a href="%s#%s" title="%s">%s</a>' % \
              (self.api_url, key, args, key)
        return groups[0] + tmp + groups[2]

    def __not_in_link(self, obj):
        groups = obj.groups()
        if not groups[0]:
            return groups[1]
        tmp = self.re_docs.sub(self.__keyword, groups[0])
        return tmp + groups[1]

    def uni(self, text):
        """Function always return unicode in Python 2 or str in Python 3."""
        if unicode_exist and isinstance(text, str):
            return text.decode(self.encoding)
        return text

    def linked_api(self, doc):
        """Append link to api to html.

        Function is called by Context.wiki or Context.rst.
        """
        if self.re_docs is not None:
            return re_notlink.sub(self.__not_in_link, doc)
        else:
            return doc

    def load_module(self, module):               # jinja function
        """Get documentation of function, variables and classes from module.

        Example:

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

        if '__file__' in module.__dict__:
            _file = module.__file__
        else:
            _file = module.__name__

        if _file in self.modules:
            return []
        else:
            self.modules.append(_file)

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
                    dependences.add(item.__module__)
                    continue
                # type, name, args, doc
                doc.append(('class',
                            self.uni(item.__name__),
                            None,
                            self.uni(getdoc(item) or '')))

                for nm, it in getmembers(item):     # class members
                    if ismethod(it) or isfunction(it) \
                            or ismethoddescriptor(it) \
                            or isgetsetdescriptor(it):
                        try:
                            mtype = 'descriptor'
                            if sys.version_info[0] > 2:     # python 3.x
                                if isfunction(it):
                                    mtype = 'method'
                                elif isinstance(it, staticmethod):
                                    mtype = 'staticmethod'
                            else:                           # python 2.x
                                if ismethod(it):
                                    mtype = 'method'
                                elif isfunction(it):
                                    mtype = 'staticmethod'

                            if isinstance(it, staticmethod):  # python 3.x
                                it = it.__func__

                            args, vargs, kwords, defaults = getargspec(it)
                            if defaults:
                                # transport functions to their names
                                ndefaults = []
                                for d in defaults:
                                    if isfunction(d):
                                        ndefaults.append(
                                            Fn(".".join((d.__module__,
                                                         d.__name__))))
                                    elif ismethod(d):
                                        ndefaults.append(
                                            Fn(".".join((d.__objclass__,
                                                         d.__name__))))
                                    else:
                                        ndefaults.append(d)
                                defaults = ndefaults

                            # type, name, args, doc
                            doc.append((
                                mtype,
                                (self.uni(item.__name__) + '.' +
                                 self.uni(it.__name__)),
                                formatargspec(args, vargs, kwords,
                                              defaults),
                                getdoc(it) or ''))
                        except:
                            pass

                    elif isinstance(it, property):
                        # type, name, property info, doc
                        doc.append((
                            'property',
                            self.uni(item.__name__) + '.' + self.uni(nm),
                            (bool(it.fget), bool(it.fset), bool(it.fdel)),
                            getdoc(it) or ''))
                    # elif isbuiltin(it):    <- __new__, __subclasshook__
                    else:
                        pass

            # module function
            elif isfunction(item) or isroutine(item):
                if module.__name__ != item.__module__:
                    item__module__ = item.__module__
                    if item.__module__ is None:
                        item__module__ = "None"
                    elif item.__module__.startswith(module.__name__):
                        item__module__ = \
                            item__module__[len(module.__name__)+1:]
                    # append to dependences
                    dependences.add(item__module__)
                    continue

                if not isbuiltin(item):
                    args, vargs, kwords, defaults = getargspec(item)
                    if defaults:
                        # transport functions to their names
                        ndefaults = []
                        for d in defaults:
                            if isfunction(d):
                                ndefaults.append(
                                    Fn(".".join((d.__module__,
                                                 d.__name__))))
                            elif ismethod(d):
                                ndefaults.append(
                                    Fn(".".join((d.__objclass__,
                                                 d.__name__))))
                            else:
                                ndefaults.append(d)
                        defaults = ndefaults

                    # type, name, args, doc
                    doc.append(('function',
                                name,
                                formatargspec(args, vargs, kwords,
                                              defaults),
                                getdoc(item) or ''))
                else:
                    bdoc = getdoc(item) or ''
                    if bdoc.find(name) == 0:
                        eol = bdoc.find('\n')
                        args = bdoc[len(name):eol]
                        bdoc = bdoc[eol:].strip()
                    else:
                        args = ''

                    # type, name, args, doc
                    doc.append(('function', name, args, bdoc))

            elif ismodule(item):
                doc.append(('submodule', name, None, ''))
            elif isinstance(item, Pattern):
                if name[0:2] == '__' \
                        or not re.search("\n%s\s*=" % name, source):
                    continue
                match = re.search("\n#\s*([^\n]*)\n%s\s*=" % name, source)
                comment = match.groups()[0] if match else ''
                # type, name, value, doc
                doc.append(('variable',
                            name,
                            "(%s, %s)" % (item.pattern, item.flags),
                            comment))
            else:
                if name[0:2] == '__' \
                        or not re.search("\n%s\s*=" % name, source):
                    if name in ('__author__', '__date__', '__version__'):
                        modinfo[name.strip('_')] = repr(item)
                    continue
                # get last previous comment start with hash char (#)
                match = re.search("\n#\s*([^\n]*)\n%s\s*=" % name, source)
                comment = match.groups()[0] if match else ''
                # type, name, value, doc
                doc.append(('variable', name, repr(item), comment))
        # endfor

        doc.append(('module',
                    module.__name__,
                    (modinfo['author'], modinfo['date'],
                     modinfo['version']),
                    getdoc(module) or ''))

        for name in dependences:
            doc.append(('dependence', name, None, ''))

        return sorted(doc, key=key_doc)
    # enddef loadmodule

    def keywords(self, api, api_url="",                 # jinja function
                 types=('module', 'class', 'method', 'staticmethod',
                        'descriptor', 'property', 'variable', 'function',
                        'h1', 'h2', 'h3')):
        """
        Fill internal api_url variable from names of modules, classes,
        functions, methods, variables or h1, h2 and h3 sections. With this,
        wiki can create links to this functions  or classes.

            #!jinja
            {% set api = load_module('module') %}

            {# create api rexex for from module where api will be on
               module_api.html #}
            {% do keywords(api, 'module_api.html') %}

            {# create api rexex from module where api will be on same page #}
            {% do keywords(api) %}

            {# another way how to call keywords function without do keyword #}
            {{ keywords(api) }}    {# keywords function return empty string #}

        Nice to have: there could be nice, if will be arguments in title, so
        mouseover event show some little detail of functions, methods or
        variables.
        """
        api = sorted(api, key=itemgetter(1), reverse=True)
        # TODO: dict for mapping names to parametres (for title in href)

        self.re_docs = re.compile(
            r"(\b)(%s)(\b)" % '|'.join(
                (name.replace('.', '\.')
                    for type, name, args, doc in api if type in types)))
        if self.re_docs.pattern == r"(\b)()(\b)":  # no keywrods found
            self.re_docs = None
        self.api_url = api_url

        self.api_keywords = dict(
            (name, (args if type != 'module' else None) or type)
            for type, name, args, doc in api)

        return ''
    # enddef


# endclass
