import pytest

from jinja24doc.wiki import wiki


def test_bold():
    html = wiki("*bold text*")
    assert (html == '<b>bold text</b>')

def test_source_code():
    doc = """Some line\n\n    indented line"""
    html = """Some line\n<pre class="python">    indented line</pre>"""
    assert( html == wiki(doc))
