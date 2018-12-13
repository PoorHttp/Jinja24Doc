#!/usr/bin/python

from distutils.core import Command
from distutils.command.build_scripts import build_scripts
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.dir_util import remove_tree
from distutils import log

from os import path, walk
from shutil import copyfile

from setuptools import setup

from jinja24doc import __version__


def doc():
    """Return README.rst content."""
    with open("README.rst", "r") as readme:
        return readme.read().strip()


def find_data_files(directory, target_folder=""):
    """Generate tuple for setup data_files argument."""
    rv = []
    for root, dirs, files in walk(directory):
        if target_folder:
            rv.append((target_folder+root[len(directory):],
                       list(root + '/' + f
                            for f in files if f[0] != '.' and f[-1] != '~')))
        else:
            rv.append((root,
                       list(root + '/' + f
                            for f in files if f[0] != '.' and f[-1] != '~')))
    return rv


class build_doc(Command):
    description = "build html documentation"
    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build.build-base')"),
        ('build-doc=', 'd', "directory to build html documentation to"),
        ('public', 'p', "build as part of public poorhttp web")
    ]

    def initialize_options(self):
        self.build_base = None
        self.build_doc = None
        self.public = False

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'))
        if self.build_doc is None:
            self.build_doc = path.join(self.build_base, 'doc')

    def run(self):
        from jinja24doc.context import Context
        import sys
        sys.path.insert(0, 'jinja24doc')
        log.info("creating documentation")

        def _jinja24doc(tname):
            ctx = Context(('templates/jinja24doc', 'doc'))
            log.info('jinja24doc processing %s ...' % tname)
            data = ctx.generate(tname, public=self.public)
            if not isinstance(data, str):
                data = data.encode('utf-8')
            with open(self.build_doc+'/'+tname, 'w') as out:
                out.write(data)

        log.info("building html documentation")
        if self.public:
            log.info("building as public part of poorhttp web")
        if self.dry_run:
            return
        if self.build_doc is None:
            return

        self.mkpath(self.build_doc)
        _jinja24doc('index.html')
        _jinja24doc('tools.html')
        _jinja24doc('templates.html')
        _jinja24doc('api.html')
        _jinja24doc('licence.html')
        copyfile('templates/green.css', self.build_doc+'/style.css')
        copyfile('templates/jinja24doc/web.css', self.build_doc+'/web.css')
        copyfile('templates/jinja24doc//small-logo.png',
                 self.build_doc+'/small-logo.png')


class X_build(build):
    sub_commands = build.sub_commands + [('build_doc', lambda self: True)]


class X_clean(clean):
    user_options = clean.user_options + [
        ('build-doc=', 'd', "directory to build html documentation to"),
    ]

    def initialize_options(self):
        clean.initialize_options(self)
        self.build_doc = None

    def finalize_options(self):
        clean.finalize_options(self)
        if self.build_doc is None:
            self.build_doc = path.join(self.build_base, 'doc')

    def run(self):
        if self.all:
            for directory in (self.build_doc, 'build/_scripts_'):
                if path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it",
                             directory)
        clean.run(self)


setup(
    name="jinja24doc",
    version=__version__,
    description="Jinja24Doc for Python",
    author="Ondrej Tuma",
    author_email="mcbig@zeropage.cz",
    url="http://poorhttp.zeropage.cz/jinja24doc",
    packages=['jinja24doc'],
    data_files=(
        [('share/doc/jinja24doc', ['LICENCE', 'README.rst'])] +
        find_data_files('doc', 'share/doc/jinja24doc') +
        find_data_files('build/doc', 'share/doc/jinja24doc/html') +
        find_data_files('templates', 'share/jinja24doc/templates')),
    license="BSD",
    long_description=doc(),
    classifiers=[
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
    install_requires=['jinja2 >= 2.10', 'docutils-tinyhtmlwriter'],
    test_suite='tests',
    cmdclass={'build': X_build,
              'clean': X_clean,
              'build_doc': build_doc},
    entry_points={
        'console_scripts': [
            'jinja24doc = jinja24doc.tools:jinja24doc',
            'rst24doc = jinja24doc.tools:rst24doc',
            'wiki24doc = jinja24doc.tools:wiki24doc',
        ]
    }
)
