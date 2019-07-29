What is Jinja24Doc
------------------
Jinja24Doc is lightweight documentation generator for python modules with
jinja2 templates. It is part of **Poor Http** group tools (WSGI connector,
WSGI/HTTP Server and mod_python connector). It could load modules and gets
documentation for its items. No configuration is needed, only jinja2
templates. Your or from jinja2doc package.

It is more **powerful pydoc**, with style what you want. You can format
your documentation string with some simple chars by wiki formating, which
is similar to *AsciiDoc*. Or you can use standard reStructuredText format. Both
of these markups parsers support **highlighting** and creating automatic links
to **PEP**.

Documentation in few seconds
----------------------------
There are three tools for your usage:
`rst24doc <http://poorhttp.zeropage.cz/jinja24doc_tools.html#rst24doc>`_,
`wiki24doc <http://poorhttp.zeropage.cz/jinja24doc_tools.html#wiki24doc>`_ and
`jinja24doc <http://poorhttp.zeropage.cz/jinja24doc_tools.html#jinja24doc>`_.
You can generate simple page like this with tools rst24doc and wiki24doc in
one command:

.. code-block:: bash

    # if your module use reStructuredText formating in documentation strings
    ~$ rst24doc -O your_module.html --embed-stylesheet your_module.py
    # or if your module use wiki formating in documentation strings
    ~$ rst24doc -O your_module.html --embed-stylesheet your_module.py

Or you can create your own template, which import predefined templates from
Jinja24doc. Your ``template.html`` could see like this:

.. code-block:: jinja

    {% set title = 'Your Module' %}
    {% set api = load_module('your_module') %}
    {% include '_reference.html' %}

Than call the jinja24doc tool with right parameters from path where your
python module is available:

.. code-block:: bash

    ~$ jinja24doc --embed-stylesheet template.html > your_module.html

Jinja24doc as library
---------------------
There are three submodules which you could interest to:

* `apidoc <http://poorhttp.zeropage.cz/jinja24doc_api.html#apidoc>`_ which
  contains base ApiDoc class to read python modules and create list of module
  items by method load_module.
* `rst <http://poorhttp.zeropage.cz/jinja24doc_api.html#rst>`_ which contains
  Rst class based on ApiDoc to parse reStructuredText __doc__ or document.
* `wiki <http://poorhttp.zeropage.cz/jinja24doc_api.html#wiki>`_ which contains
  Wiki class based on ApiDoc to parse wiki formated __doc__ or document.
* `context <http://poorhttp.zeropage.cz/jinja24doc_api.html#context>`_ which
  contains Context class based on Rst and Wiki to couple all functionality
  to working with jinja2 templates.
* `frontend <http://poorhttp.zeropage.cz/jinja24doc_api.html#frontend>`_ which
  contains some functions to easier create command tool like rst24doc, wiki24doc
  and jinja24doc.

Getting Jinja24doc
~~~~~~~~~~~~~~~~~~
Jinja24Doc needs Jinja2, docutils and distutils-tinyhtmlwriter package for
build and or for install. So you must install it first.

Source tarball

.. code-block:: sh

    ~$ wget https://pypi.python.org/packages/source/j/jinja24doc/jinja24doc-1.3.3.tar.gz
    ~$ tar xzf jinja24doc-1.3.3.tar.gz
    ~$ cd jinja24doc-1.3.3
    ~$ python setup.py install

Source from git
~~~~~~~~~~~~~~~
.. code-block:: sh

    ~$ git clone https://github.com/PoorHttp/Jinja24Doc.git
    ~$ cd Jinja24Doc
    ~$ python setup.py install

Install from PyPI
~~~~~~~~~~~~~~~~~

.. code-block:: sh

    ~$ pip install jinja24doc

Unstable version
~~~~~~~~~~~~~~~~
From git unstable branch:

.. code-block:: sh

    ~$ git clone clone https://github.com/PoorHttp/Jinja24Doc.git
    ~$ cd Jinja24Doc
    ~$ git checkout unstable
    ~$ python setup.py install

or from zip package:

.. code-block:: sh

    ~$ wget https://github.com/PoorHttp/Jinja24Doc/archive/unstable.zip
    ~$ unzip unstable.zip
    ~$ cd Jinja24Doc-unstable
    ~$ python setup.py install
