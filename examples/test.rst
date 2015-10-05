Jinja24Doc reStructuredText test
================================

Paragraph
---------
So this is sime Jinja24Doc reStructuredText test. First, we test some text
paragraphs with base formating like *emphasis*, **strong**, `interpreted text`,
``monospaced text`` and normal external hyperlink to `Jinja24Doc
<http://jinja24doc.zeropage.cz>`_

Lists
-----
Sometime, there will be lists in documentation:
    * first
    * second

Codes
-----
code blocks with syntax
.......................
.. code-block:: python

    @decorator(*args):
    def function(param, **kwargs):
        """ __doc__ for function """
        if param is None:
            raise Exception("Param can't be None")
        assert (isinstance(param, int))
        value = param * 2       # some work
        return value

    try:
        function()
    except Exception as e:
        print(e)

code blocks with line numbers
.............................
.. code::
    :number-lines:

    This code block text formated in pre with
    numer of each lines. So that is really cool
    functionality, yes !

doctest code
............
Doctest code is not highlited by default from rst, but,
Jinja24Doc can do that. For examle see the last code, but in doctest
mode:

>>> @decorator(*args):
>>> def function(param, **kwargs):
>>>     """ __doc__ for function """
>>>     if param is None:
>>>         raise Exception("Param can't be None")
>>>     assert (isinstance(param, int))
>>>     value = param * 2       # some work
>>>     return value
>>>
>>>  try:
>>>     function()
>>>  except Exception as e:
>>>     print(e)
Exception: Param can't be None

Indent block
............

    This is indent block, which is formated as block
    only by indenting in source.

And this is process as normal text and as python documentation of module for
example now. :)
