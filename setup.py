#!/usr/bin/python

from distutils.core import setup
from distutils.command.build_scripts import build_scripts
from distutils.command.build import build

from os import path, makedirs
from shutil import copyfile

class X_build_scripts(build_scripts):
    def run(self):
        if not path.exists('build/_scripts_'):
            makedirs('build/_scripts_')
        copyfile('jinja24doc.py', 'build/_scripts_/jinja24doc')
        build_scripts.run(self)     # run original build

class X_build(build):
    def run(self):
        import jinja24doc
        jinja24doc.paths = ('templates', 'doc')
        print "creating documentation"
        def _jinja24doc(tname, oname):
            jinja24doc.re_docs = None
            jinja24doc._api_url = ''
            jinja24doc._api_keywords = {}
            jinja24doc._modules = []
            print 'jinja24doc processing %s ...' % oname
            data = jinja24doc._generate(tname, jinja24doc.paths)
            if not isinstance(data, str):
                data = data.encode('utf-8')
            with open(oname, 'w') as f:
                f.write(data)
        
        if not path.exists('build/_html_'):
            makedirs('build/_html_')
        _jinja24doc('_jinja24doc.html',     'build/_html_/index.html')
        _jinja24doc('_jinja24doc_api.html', 'build/_html_/jinja24doc_api.html')
        _jinja24doc('_licence.html',        'build/_html_/licence.html')
        copyfile('templates/style.css',     'build/_html_/style.css')
        build.run(self)             # run original build


setup(
    name                = "jinja24doc",
    version             = "1.0",
    description         = "Jinja24Doc for Python",
    author              = "Ondrej Tuma",
    author_email        = "mcbig@zeropage.cz",
    url                 = "http://poorhttp.zeropage.cz/jinja24doc.html",
    scripts             = ['build/_scripts_/jinja24doc'],
    data_files          = [
                ('share/doc/jinja24doc', ['doc/readme.txt', 'doc/licence.txt']),
                ('share/doc/jinja24doc/html',
                        ['build/_html_/index.html',
                         'build/_html_/jinja24doc_api.html',
                         'build/_html_/licence.html',
                         'build/_html_/style.css']),
                ('share/jinja24doc/templates',
                        ['templates/_simple.html',
                         'templates/_simple_with_submodules.html'])],
    license             = "BSD",
    long_description    =
    """
    Jinja24doc is lightweight documentation generator for python modules
    with jinja2 templates. It is part of *Poor Http* group tools (WSGI
    connector, WSGI/HTTP Server and mod_python connector). It could load
    modules and gets documentation for its items. No configuration is
    needed, only jinja2 templates. Your or from jinja2doc package.
    """,
    classifiers         = [
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Natural Language :: English",
            "Natural Language :: Czech",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Topic :: Documentation",
            "Topic :: Software Development :: Documentation",
            "Topic :: Text Processing :: Markup"
    ],
    install_requires    = ['jinja2 >= 2.6'],
    cmdclass            = {'build_scripts': X_build_scripts,
                           'build': X_build },
)
