from sys import path as python_path
from os import path

python_path.insert(0, path.abspath(
    path.join(path.dirname(__file__), path.pardir)))

import pytest

from jinja24doc.wiki import Wiki


@pytest.fixture()
def ctx():
    return Wiki()


def test_bold(ctx):
    html = ctx.wiki("*bold text*")
    assert html == '<b>bold text</b>'
    html = ctx.wiki("*bold * text*")
    assert html == '<b>bold * text</b>'


def test_bold_negative(ctx):
    negatives = (
        "* bold text*",
        "* bold text *",
        "*bold text *"
    )
    for it in negatives:
        assert it == ctx.wiki(it)


def test_italic(ctx):
    html = ctx.wiki("/italic text/")
    assert html == '<i>italic text</i>'
    html = ctx.wiki("/k/")
    assert html == '<i>k</i>'


def test_italics_negative(ctx):
    negatives = (
        "/ italic/",
        "/ italic /",
        "/italic /"
    )
    for it in negatives:
        assert it == ctx.wiki(it)


def test_monospace(ctx):
    html = ctx.wiki("{one} and {two}")
    assert html == '<code>one</code> and <code>two</code>'
    html = ctx.wiki("{/one}")
    assert html == '<code>/one</code>'
    html = ctx.wiki("{/one}")
    assert html == '<code>/one</code>'
    html = ctx.wiki("is {On},")
    assert html == 'is <code>On</code>,'
    html = ctx.wiki("is {On}, text\n{/debug-info} page")
    assert html == 'is <code>On</code>, text\n<code>/debug-info</code> page'
    html = ctx.wiki("{test}.")
    assert html == "<code>test</code>."


def test_link(ctx):
    html = ctx.wiki("http://x.y/abc")
    assert html == '<a href="http://x.y/abc">http://x.y/abc</a>'
    html = ctx.wiki("http://abc/d.")
    assert html == '<a href="http://abc/d">http://abc/d</a>.'


def test_combinate(ctx):
    html = ctx.wiki("{/xx/}")
    assert html == '<code>/xx/</code>'


def test_source_code(ctx):
    doc = """Some line\n\n    indented line"""
    html = """Some line\n<pre class="python">    indented line</pre>"""
    assert(html == ctx.wiki(doc))
