#!/usr/bin/python

from distutils.core import setup
from os import path, makedirs
from shutil import copyfile
from subprocess import call

if not path.exists('build/_scripts_'):
    makedirs('build/_scripts_')
copyfile('jinja24doc.py', 'build/_scripts_/jinja24doc')

if not path.exists('build/_html_'):
    makedirs('build/_html_')
call(['./jinja24doc.py', '_jinja24doc.html', 'templates:doc'],
                        stdout=file('build/_html_/index.html', 'w'))
call(['./jinja24doc.py', '_jinja24doc_api.html', 'templates:doc'],
                        stdout=file('build/_html_/jinja24doc_api.html', 'w'))
call(['./jinja24doc.py', '_licence.html', 'templates:doc'],
                        stdout=file('build/_html_/licence.html', 'w'))
copyfile('templates/style.css', 'build/_html_/style.css')


setup(
    name                = "jinja24doc",
    version             = "1.0",
    description         = "Jinja24Doc for Python",
    author              = "Ondrej Tuma",
    author_email        = "mcbig@zeropage.cz",
    url                 = "http://poorhttp.zeropage.cz/jinja24doc.html",
    scripts             = ['build/_scripts_/jinja24doc'],
    data_files          = [
                ('share/doc/jinja24doc',
                        ['doc/readme.txt', 'doc/licence.txt']),
                ('share/doc/jinja24doc/html',
                        ['build/_html_/*', 'templates/style.css']),
                ('share/jinja24doc/templates',
                        ['templates/*'])],
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
            "Topic :: Documentation",
            "Topic :: Software Development :: Documentation",
            "Topic :: Text Processing :: Markup"
    ],
    install_requires    = ['jinja2 >= 2.6'],
)
