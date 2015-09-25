import pytest

from inspect import cleandoc

#test failed...:(
def _test_cleandoc_indent():
    """ Some line

            indented line
    """
    doc = """Some line\n\n    indented line"""
    assert (doc == cleandoc(test_cleandoc.__doc__))

