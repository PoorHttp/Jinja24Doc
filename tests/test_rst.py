from jinja24doc.rst import rst

from inspect import cleandoc

def test_simple():
    assert "simple" == rst("simple")

def test_more():
    doc = "first line\n\nsecond line"
    html = "<p>first line</p>\n\n<p>second line</p>"
    assert html == rst(doc)

def test_header():
    """
    Header
    ======
    Text
    """
    assert '<a name="header"></a><h1>Header</h1>\n<p>Text</p>' == rst(cleandoc(test_header.__doc__))

def test_file():
    with open ('examples/test.rst') as src:
        doc = src.read()
    with open ('examples/out/test.html', 'w+') as out:
        out.write(rst(doc))

if __name__ == '__main__':
    test_simple()
    test_more()
