from jinja24doc.rst import Rst

from inspect import cleandoc


def test_simple():
    rst = Rst()
    assert "simple" == rst.rst("simple")


def test_more():
    doc = "first line\n\nsecond line"
    html = "<p>first line</p>\n\n<p>second line</p>"
    rst = Rst()
    assert html == rst.rst(doc)


def test_header():
    """Testing header

    Header
    ------
    Text
    """
    rst = Rst()
    assert '<p>Testing header</p>\n\n\n<a name="header"></a><h1>Header</h1>\n<p>Text</p>' == \
           rst.rst(cleandoc(test_header.__doc__), section_level=0)


def test_pep257():
    """This is PEP257 formated documentation.

    So question is, how it will be formated.
    """
    rst = Rst()
    assert '<p>This is PEP257 formated documentation.</p>\n\n' + \
           '<p>So question is, how it will be formated.</p>' == \
           rst.rst(cleandoc(test_pep257.__doc__))


def test_file():
    with open('examples/test.rst') as src:
        doc = src.read()
    rst = Rst()
    with open('examples/out/test.html', 'w+') as out:
        out.write(rst.rst(doc))

if __name__ == '__main__':
    test_simple()
    test_more()
