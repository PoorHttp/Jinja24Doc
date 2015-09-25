from jinja24doc.rst import rst

def test_simple():
    assert("simple" == rst("simple"))

def test_more():
    doc = "first line\n\nsecond line"
    html = "<p>first line</p>\n\n<p>second line</p>"
    assert(html == rst(doc))

if __name__ == '__main__':
    test_simple()
    test_more()
