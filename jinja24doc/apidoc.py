""" module api documentation reader """

from inspect import getargspec, getdoc, getmembers, getsource, formatargspec, \
    isfunction, isroutine, ismethod, isclass, ismodule, isbuiltin, \
    ismethoddescriptor, isgetsetdescriptor
from operator import itemgetter
from os import path

import sys
import re

from jinja24doc.misc import uni

_ordering = {'module':       (0, 0),
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
TEMPLATES = "/share/jinja24doc/templates/"


class G(object):
    """ Global variables class """
    paths = ['/usr/local%s' % TEMPLATES,
             path.abspath(path.join(path.dirname(__file__),
                                    path.pardir+TEMPLATES))]
    re_docs = None
    _api_url = ''
    _api_keywords = {}
    _modules = []

    def __init__(self):
        raise RuntimeError('G is singleton')


class Fn:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


def _key_doc(a):
    o = _ordering[a[0]]
    return str(o[0])+a[1].replace('.', str(o[1]))


def _keyword(obj):
    groups = obj.groups()
    key = groups[1]

    args = G._api_keywords[key]

    tmp = '<a href="%s#%s" title="%s">%s</a>' % \
          (G._api_url, key, args, key)
    return groups[0] + tmp + groups[2]


def _not_in_link(obj):
    groups = obj.groups()
    if not groups[0]:
        return groups[1]

    tmp = G.re_docs.sub(_keyword, groups[0])
    return tmp + groups[1]


def linked_api(doc):
    """ Function which is called by wiki or rst to append links to api. """
    return re_notlink.sub(_not_in_link, doc) if G.re_docs is not None else doc


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

    if '__file__' in module.__dict__:
        _file = module.__file__
    else:
        _file = module.__name__

    if _file in G._modules:
        return []
    else:
        G._modules.append(_file)

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
                        uni(item.__name__),                             # name
                        None,                                           # args
                        uni(getdoc(item) or '')))                       # doc

            for nm, it in getmembers(item):     # class members
                if ismethod(it) or isfunction(it) or ismethoddescriptor(it) \
                        or isgetsetdescriptor(it):
                    try:
                        mtype = 'descriptor'
                        if sys.version_info[0] > 2:         # python 3.x
                            if isfunction(it):
                                mtype = 'method'
                            elif isinstance(it, staticmethod):
                                mtype = 'staticmethod'
                        else:                               # python 2.x
                            if ismethod(it):
                                mtype = 'method'
                            elif isfunction(it):
                                mtype = 'staticmethod'

                        if isinstance(it, staticmethod):    # python 3.x
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
                            uni(item.__name__) + '.' + uni(it.__name__),
                            formatargspec(args, vargs, kwords, defaults),
                            getdoc(it) or ''))
                    except:
                        pass

                elif isinstance(it, property):
                    # type, name, property info, doc
                    doc.append((
                        'property',
                        uni(item.__name__) + '.' + uni(nm),
                        (bool(it.fget), bool(it.fset), bool(it.fdel)),
                        getdoc(it) or ''))
                # elif isbuiltin(it):    <- __new__, __subclasshook__
                else:
                    pass

        elif isfunction(item) or isroutine(item):       # module function
            if module.__name__ != item.__module__:
                item__module__ = item.__module__
                if item.__module__.startswith(module.__name__):
                    item__module__ = item__module__[len(module.__name__)+1:]
                dependences.add(item__module__)         # append to dependences
                continue

            if not isbuiltin(item):
                args, vargs, kwords, defaults = getargspec(item)
                if defaults:
                    ndefaults = []      # transport functions to their names
                    for d in defaults:
                        if isfunction(d):
                            ndefaults.append(
                                Fn(".".join((d.__module__, d.__name__))))
                        elif ismethod(d):
                            ndefaults.append(
                                Fn(".".join((d.__objclass__, d.__name__))))
                        else:
                            ndefaults.append(d)
                    defaults = ndefaults

                # type, name, args, doc
                doc.append(('function',
                            name,
                            formatargspec(args, vargs, kwords, defaults),
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
        elif isinstance(item, re._pattern_type):
            if name[0:2] == '__' or not re.search("\n%s\s*=" % name, source):
                continue
            match = re.search("\n#\s*([^\n]*)\n%s\s*=" % name, source)
            comment = match.groups()[0] if match else ''
            # type, name, value, doc
            doc.append(('variable',
                        name,
                        "(%s, %s)" % (item.pattern, item.flags),
                        comment))
        else:
            if name[0:2] == '__' or not re.search("\n%s\s*=" % name, source):
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
                (modinfo['author'], modinfo['date'], modinfo['version']),
                getdoc(module) or ''))

    for name in dependences:
        doc.append(('dependence', name, None, ''))

    return sorted(doc, key=_key_doc)


def keywords(api, api_url="",                 # jinja function
             types=('module', 'class', 'method', 'staticmethod', 'descriptor',
                    'property', 'variable', 'function', 'h1', 'h2', 'h3')):
    """
    Fill internal api_url variable from names of modules, classes,
    functions, methods, variables or h1, h2 and h3 sections. With this,
    wiki can create links to this functions  or classes.

        #!jinja
        {% set api = load_module('module') %}

        {# create api rexex for from module where api will be on
           module_api.html #}
        {% do keywords(api, 'module_api.html') %}

        {# create api rexex for from module where api will be on same page #}
        {% do keywords(api) %}

        {# another way how to call keywords function without do keyword #}
        {{ keywords(api) }}      {# keywords function return empty string #}

    Nice to have: there could be nice, if will be arguments in title, so
    mouseover event show some little detail of functions, methods or
    variables.
    """
    api = sorted(api, key=itemgetter(1), reverse=True)
    # TODO: dict for mapping names to parametres (for title in href)

    G.re_docs = re.compile(
        r"(\b)(%s)(\b)" % '|'.join(
            (name.replace('.', '\.')
                for type, name, args, doc in api if type in types)))
    if G.re_docs.pattern == r"(\b)()(\b)":  # no keywrods found
        G.re_docs = None
    G._api_url = api_url

    G._api_keywords = dict((name, (args if type != 'module' else None) or type)
                           for type, name, args, doc in api)

    return ''
