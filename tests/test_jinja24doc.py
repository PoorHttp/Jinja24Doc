from sys import path as python_path
from os import path, makedirs
from shutil import copyfile

import pytest

from jinja24doc.apidoc import G
from jinja24doc.main import _generate

def get_pathfor(arg):
    return path.normpath(path.join(path.dirname(__file__), path.pardir+'/'+arg))

EXAMPLES = get_pathfor('examples')
G.paths = (get_pathfor('templates'),EXAMPLES)

python_path.insert(0, EXAMPLES)

def jinja24doc(name):
    G.re_docs = None
    G._api_url = ''
    G._api_keywords = {}
    G._modules = []
    data = _generate('%s' % name, G.paths)
    if not isinstance(data, str):
        data = data.encode('utf-8')
    with open('%s/out/%s' % (EXAMPLES, name), 'w') as f:
        f.write(data)

@pytest.fixture(autouse = True)
def make_out():
    """ Make output directory for examples """
    try:
        makedirs('%s/out' % EXAMPLES)
    except OSError as e:
        if e.args[0] != 17:
            raise e
    copyfile(get_pathfor('templates/blue.css'), '%s/out/style.css' % EXAMPLES)

class TestWiki():
    """ Generate wiki examples """
    def test_text(self):
        jinja24doc('test_wiki.html')

    def test_module(self):
        jinja24doc('test_module_wiki.html')

    def test_module_linked(self):
        jinja24doc('test_module_wiki_linked.html')


class TestRst():
    """ Generate reStrucuredText examples """
    def test_text(self):
        jinja24doc('test_rst.html')

    def test_invalid(self):
        jinja24doc('test_rst_invalid.html')

    def test_module(self):
        jinja24doc('test_module_rst.html')

    def test_module_linked(self):
        jinja24doc('test_module_rst_linked.html')
