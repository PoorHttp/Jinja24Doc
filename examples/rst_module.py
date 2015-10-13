"""
Example module with wiki formated __doc__
==========================================
This is some example module with wiki formating __doc__. Some strings from
documentation could have links to module objects. Like to Object class,
check_number or none function.

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
            raise RuntimeError('This is singleton\\n') # raise the exception

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

Default code block:

.. code::

    try:
        raise RuntimeError('Some runtime Error')
    except Exception as e:
        print (e)

And some doctest

>>> from os import path
>>> print(path.devnull)
/dev/null

Headers in documentation
------------------------

 * Title of document (h1) is skiped
 * Other headers start on 2, which could be h1, so typical on h3
"""

def none():
    """ Function return None

    >>> print(none())
    None
    """
    return None

def check_number(val):
    """ Functin check number:
            val - input value
            return True or False

        .. code-block:: python
            :number-lines:

            from os import sys

            sys.stdout.write("Testing check number:\\n")
            sys.stdout.write("\\t12\\t:%s\\n" % check_number(12))          # True
            sys.stdout.write("\\t3.14\\t:%s\\n" % check_number(3.14))      # True
            sys.stdout.write("\\tFalse\\t:%s\\n" % check_number(False))    # False
            sys.stdout.write("\\tNone\\t:%s\\n" % check_number(None))      # False
            sys.stdout.write("\\t10**10\\t:%s\\n" % check_number(10**10))  # True
            sys.stdout.flush()
    """
    pass

class Object(object):
    """ Empty class """
    pass

class Point(Object):
    """ Point class """
    def __init__(self, x, y):
        """ Set x and y values """
        pass

    def draw(self, color = "black"):
        """ draw point with defined color
            color - color for drawing, default is black
        """

    @property
    def read_write(self):
        """ this is read and write property """
    @read_write.setter
    def read_write(self, value):
        pass

    @property
    def read_only(self):
        """ this is read only property """
        pass

# module name
module_name = "wiki module"

# defalt point at 0,0
zero = Point(0,0)

