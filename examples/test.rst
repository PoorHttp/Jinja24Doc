Jinja24Doc reStructuredText test
================================

Paragraph
---------
So this is some Jinja24Doc reStructuredText test. First, we test some text
paragraphs with base formating like *emphasis*, **strong**, `interpreted text`,
``monospaced text`` and normal external hyperlink to `Jinja24Doc
<http://jinja24doc.zeropage.cz>`_

Lists
-----
Sometime, there will be lists in documentation:
    * first
    * second

Images
------
.. image:: http://docutils.sourceforge.net/rst.png
    :alt: reStructuredText logo
    :name: reStructuredText logo

Now there are some simple image

.. image:: image.png

and next, here is link to `reStructuredText logo`_ image :)

And some included |C| image :)

.. |C| image:: http://smileys.emoticonsonly.com/emoticons/c/cool-1037.gif
   :height: 11
   :width: 11
   :alt: C

Codes
-----
code blocks with syntax
.......................
.. code-block:: python

    # simple python exmple in code-block (python)
    from cool import notcool

    class Object(object):
       ''' Class documentation '''
        none = None
        true = True
        false = False
        n = int(10)
        s = str('text')

        def __init__(self):
            raise RuntimeError('This is singleton\n') # raise the exception

    try:
        obj = Object()
    except Exception as e:
        print(e)

    class Foo(Object):
        @staticmethod
        def info():
            return "This is foo \u010d"

    for i in range(100):
        if i > 10 and i < 50:
            print (i*i)

code blocks with line numbers
.............................
This is `Simple code`_ :).

.. code::
    :number-lines:
    :name: Simple code

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
