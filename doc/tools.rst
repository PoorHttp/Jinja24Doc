There are some command tools for use. You can call this tools directly for
generate your documentation page from source code or source template.

jinja24doc
----------
jinja24doc is command for processing templates. You can read how templates
looks and what functions are you can call at extra
`template page <jinja24doc_templates.html>`_. In short, you can use create one
simple template ``template.html`` like this:

.. code-block:: jinja

    {% set title = 'Your Python Module' %}
    {% set api = load_module('your_python_module') %}
    {% include '_reference.html' %}

and next, call the jinja24doc tool with parameter of your template filename:

::

    ~$ jinja24doc template.html > page.html

If you want to import modules from your package, which are not installed on
system, or which are not in actual directory, you must set PYTHONPATH
environment variable. Next example extend module search path to ./falias,
./morias and ./poorwsgi directories:

::

    ~$ PYTHONPATH=falias:morias:poorwsgi jinja24doc template.html > page.html

Tool automatically find templates in local path, and system templates path
(``/usr/local/share/jinja24doc/templates``), or you can use path as second
parameters.

At this moment, jinja24doc can set files encoding, stylesheet, included
stylesheet, top and link using. For more details use jinja24doc see help output
(``--help`` option).

rst24doc
--------
rst24doc command tool is tool like rst2html, but use jinja24doc. So it could
generate documentation page direct from python module (file) or from
reStructured text. Internally, rst24doc use ``module.html`` and ``text.html``
template. Using is simple as could be, type only:

.. code-block:: sh

    ~$ rst24doc document.rst > document.html    # for documentation page from text
    ~$ rst24doc module.py > module.html         # for documentation page from module

Tool options are the same as jinja24doc. So you can configure some runtime
variables like top, link, encoding etc.

wiki24doc
---------
wiki24doc command tool is tool like rst24doc, but use wiki formating documentation
source. Wiki formating using in Jinja24doc is like AsciiDoc and may be it could be
replace in future. Tool use same internal templates like rst24doc and the same
option interface. See little example:

.. code-block:: sh

    ~$ wiki24doc document.wiki > document.html  # for documentation page from text
    ~$ wiki24doc module.py > module.html        # for documentation page from module
