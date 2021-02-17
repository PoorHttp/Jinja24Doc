from sys import path as python_path
from os import path, makedirs
from shutil import copyfile

from mock import patch
import pytest  # type: ignore

python_path.insert(0, path.abspath(
    path.join(path.dirname(__file__), path.pardir)))

from jinja24doc.context import Context


def get_pathfor(arg):
    return path.normpath(path.join(path.dirname(__file__),
                                   path.pardir+'/'+arg))

EXAMPLES = get_pathfor('examples')
python_path.insert(0, EXAMPLES)


def _jinja24doc(name):
    ctx = Context((get_pathfor('templates'), EXAMPLES))
    data = ctx.generate('%s' % name)
    if not isinstance(data, str):
        data = data.encode('utf-8')
    with open('%s/out/%s' % (EXAMPLES, name), 'w') as f:
        f.write(data)


@patch('jinja24doc.apidoc.sys.stderr')
def jinja24doc(name, mock):
    _jinja24doc(name)
    for it in mock.method_calls:
        print (it)
    assert len(mock.method_calls) == 0


@patch('jinja24doc.apidoc.sys.stderr')
def negative_jinja24doc(name, mock):
    _jinja24doc(name)
    assert len(mock.method_calls) > 0


@pytest.fixture(autouse=True)
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
        negative_jinja24doc('test_rst_invalid.html')

    def test_module(self):
        jinja24doc('test_module_rst.html')

    def test_module_linked(self):
        jinja24doc('test_module_rst_linked.html')

if __name__ == "__main__":
    for c in (TestWiki, TestRst):
        o = c()
        for m in dir(o):
            if m.startswith('test_'):
                print ('%s::%s' % (c.__name__, m))
                getattr(o, m)()
