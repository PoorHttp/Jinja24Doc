#!/usr/bin/python

# try:
#   can't use setuptools yet, becouse i found data file in absolute path
#    from setuptools import setup
# except:
from distutils.core import setup

from distutils.command.build_scripts import build_scripts
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.dir_util import remove_tree
from distutils import log

from os import path, walk
from shutil import copyfile

from jinja24doc import __version__


def find_data_files(directory, targetFolder=""):
    """Create datafiles from directory tree."""
    rv = []
    for root, dirs, files in walk(directory):
        if targetFolder:
            location = (targetFolder+root.lstrip(directory)).rstrip('/')
            rv.append((location,
                       list(root+'/'+f
                            for f in files if f[0] != '.' and f[-1] != '~')))
        else:
            rv.append((root,
                       list(root+'/'+f
                            for f in files if f[0] != '.' and f[-1] != '~')))
    log.info(str(rv))
    return rv


class X_build_scripts(build_scripts):
    def run(self):
        self.mkpath('build/_scripts_')
        copyfile('jinja24doc.py', 'build/_scripts_/jinja24doc')
        copyfile('rst24doc.py', 'build/_scripts_/rst24doc')
        copyfile('wiki24doc.py', 'build/_scripts_/wiki24doc')
        build_scripts.run(self)     # run original build


class X_build(build):
    def run(self):
        from jinja24doc.context import Context
        import sys
        sys.path.insert(0, 'jinja24doc')
        log.info("creating documentation")

        def _jinja24doc(tname, oname):
            ctx = Context(('templates/jinja24doc', 'doc'))
            log.info('jinja24doc processing %s ...' % oname)
            data = ctx.generate(tname)
            if not isinstance(data, str):
                data = data.encode('utf-8')
            with open(oname, 'w') as f:
                f.write(data.replace('http://poorhttp.zeropage.cz/', ''))

        self.mkpath('build/_html_')
        _jinja24doc('index.html',
                    'build/_html_/index.html')
        _jinja24doc('jinja24doc_tools.html',
                    'build/_html_/jinja24doc_tools.html')
        _jinja24doc('jinja24doc_templates.html',
                    'build/_html_/jinja24doc_templates.html')
        _jinja24doc('jinja24doc_api.html',
                    'build/_html_/jinja24doc_api.html')
        _jinja24doc('jinja24doc_licence.html',
                    'build/_html_/jinja24doc_licence.html')
        copyfile('templates/green.css', 'build/_html_/style.css')
        build.run(self)             # run original build


class X_clean(clean):
    def run(self):
        for directory in ('build/_html_', 'build/_scripts_'):
            if path.exists(directory):
                remove_tree(directory, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it",
                         directory)
        clean.run(self)

kwargs = {
    'name':             "jinja24doc",
    'version':          __version__,
    'description':      "Jinja24Doc for Python",
    'author':           "Ondrej Tuma",
    'author_email':     "mcbig@zeropage.cz",
    'url':              "http://poorhttp.zeropage.cz/jinja24doc.html",
    'packages':         ['jinja24doc'],
    'scripts':          ['build/_scripts_/jinja24doc',
                         'build/_scripts_/rst24doc',
                         'build/_scripts_/wiki24doc'],
    'data_files':
        [('share/doc/jinja24doc', ['LICENCE', 'README.rst'])] +
        find_data_files('doc', 'share/doc/jinja24doc') +
        find_data_files('build/_html_', 'share/doc/jinja24doc/html') +
        find_data_files('templates', 'share/jinja24doc/templates'),
    'license':           "BSD",
    'long_description':
    """
    Jinja24doc is lightweight documentation generator for python modules
    with jinja2 templates. It is part of Poor Http group tools (WSGI
    connector, WSGI/HTTP Server and mod_python connector). It could load
    modules and gets documentation for its items. No configuration is
    needed, only jinja2 templates. Your or from jinja2doc package.
    """,
    'classifiers':      [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Natural Language :: Czech",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities"
    ],
    'install_requires': ['jinja2 >= 2.6', 'docutils-tinyhtmlwriter'],
    'test_suite':        'tests',
    'cmdclass':           {'build_scripts': X_build_scripts,
                           'build': X_build,
                           'clean': X_clean},
}

setup(**kwargs)
