"""Library use context object"""

from jinja2 import Environment, FileSystemLoader

from sys import stderr
from os import path, getcwd

from jinja24doc.apidoc import local_name, property_info
from jinja24doc.wiki import Wiki
from jinja24doc.rst import Rst

TEMPLATES = "../../../../share/jinja24doc/templates/"


def log(message):
    """
    Write message to stderr.

        #!jinja
        {% do log('some debug message') %}
    """
    stderr.write("%s\n" % message)


class Context(Wiki, Rst):

    def __init__(self, paths, encoding='utf-8'):
        super(Context, self).__init__()
        if isinstance(paths, tuple):
            paths = list(paths)
        assert isinstance(paths, list), "Paths is %s" % paths.__class__
        self.paths = paths + [getcwd(),
                              path.abspath(path.join(path.dirname(__file__),
                                                     TEMPLATES))]
        self.encoding = encoding

    def prepare_environment(self):
        """Prepare jinja2 environment.

        This method is called internal by Context.generate method, and append
        Conetxt methods to jinja2 template globals. So Context.load_module,
        Context.keywords, local_name, property_info, wiki, Context.load_wiki,
        Context.load_text, Context.load_source, Context.rst, Context.load_rst
        and log methods and functions are enabled to call in templates.
        """
        env = Environment(loader=FileSystemLoader(self.paths),
                          trim_blocks=True,
                          extensions=['jinja2.ext.do',
                                      'jinja2.ext.loopcontrols'],
                          lstrip_blocks=True)     # add in 2.7

        env.globals['load_module'] = self.load_module
        env.globals['keywords'] = self.keywords
        env.globals['local_name'] = local_name
        env.globals['property_info'] = property_info

        env.globals['wiki'] = self.wiki
        env.globals['load_wiki'] = self.load_wiki
        env.globals['load_text'] = self.load_text
        env.globals['load_source'] = self.load_source

        env.globals['rst'] = self.rst
        env.globals['load_rst'] = self.load_rst
        env.globals['log'] = log
        return env

    def generate(self, template, **kwargs):
        """Generate html output from template."""
        env = self.prepare_environment()
        temp = env.get_template(template)
        return temp.render(**kwargs)
