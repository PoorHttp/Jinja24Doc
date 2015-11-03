The main power of Jinja2doc environment is Jinja2 templates which is use for
formating documentation output. First, Jinja2doc was be create for python modules
documentation.

Basic usage
-----------
There are few function, which is available in jinja2 templates. First two
load_module, load_rst and load_wiki returns documentation list. Function
load_wiki is deprecated alias for load_wiki.

.. code-block:: jinja

    {% set api = load_module('module') %}
    {% set rst_sections = load_rst('file.rst') %}
    {% set wiki_sections = load_wiki('file.wiki') %}

Other functions works with string, they format it. Function rst generate html
string formated with base rst syntax, wiki for wiki formated text. It know
headers, bold text, parameter padding, code block or paragraphs defined with
double newline. Both of these functions could create PEP and RFC links to api
definition. If you want to create api links, you must fill api regex variable
by keywords function first.

.. code-block:: jinja

    {% do keywords(api, 'api_page.html') %}
    {{ wiki(api[0][3]) }}   {# put to document formated first documentation #}
                            {# from api (it wold be module documentation #}

Keywords function returns empty string, so you can call it from {{ }} block.
Next, keywords rewrite internal variables api regex and api link, so in this
moment, there cant do api linking for more than one page. If you have more
than one module on one page, you can join api variable from both of them.

.. code-block:: jinja

    {% set api = load_module('first_module') %}
    {% set api = api + load_module('second_module') %}
    {% do keywords(api, 'api_page.html') %}
    {{ wiki(api[0][3]) }}

Public templates
~~~~~~~~~~~~~~~~
There are some public templates, which you can find in
``share/jinja24doc/templates`` directory.

``module.html``
    This template is use by rst24doc and wiki24doc command tools
    to generate documentation from python module by one command.

``text.html``
    Like module.html, but for generate documentation from text
    source file.

``_simple.html``
    Simple html web page. Style is included.

``_simple_with_submodules.html``
    Simple html web page. Style is included. All submodules are included
    recursive. This could be demo, how you can generate manual from your code
    recursively.

``_reference.html``
    This template generates html pages looks like Jinja24Doc manual. There are
    some different styles:``red.css, blue.css, green.css, gray.css`` and
    ``inverse.css`` which you can use with this template. You must only copy to
    output directory as style.css ;) ``_reference.html`` template is used in
    ``module.html``

``_text.html``
    This template looks like ``_reference.html``, but it is prepare to generate
    html page from text. This template needs **sections** instead of api variable,
    which looks contain data generate from text file. See to Context.load_rst or
    Context.load_wiki functions.

    Like reference.html template, this use styles too, so You must only copy to
    output directory as style.css too.

Data structure
--------------
The documentation list which returns functions load_module, load_rst and
load_wiki looks like that:

.. code-block:: python

    ((type, name, args, documentation),)    # all values are strings

Of course, some items don't have all values, so on their place is None or
another value, typical for their type. Modules could have author, date and version,
if it available. Submodules, do not have documentation. Dependences are modules,
which is not import, but there is import some routines from that. And variables
jave value instead of arguments. If you want to doing documentation for it, that is
comment on one line before. Next list is typical for load_module
function.

.. code-block:: python

    (('module', 'name', ('author', 'date', 'version'), 'documentation'),
     ('submodule', 'name', None, ''),
     ('dependence', 'name', None, ''),
     ('class', 'ClassName', None, 'documentation'),
     ('property', 'ClassName.name', (READ, WRITE, DELETE), 'documentation')),
     ('descriptor', 'ClassName.name', args, 'documentation')),
     ('method', 'ClassName.name', args, 'documentation')),
     ('staticmethod', 'ClassName.name', args, 'documentation')),
     ('function', 'name', args, 'documentation'),
     ('variable', 'name', value, 'documentation'))

For load_rst and load_wiki function is this typical list:

.. code-block:: python

    (('h1', 'title', None, ''),     # = title =
     ('h2', 'title', None, ''),     # == title ==
     ('h3', 'title', None, ''),     # === title ===
     ('h4', 'title', None, ''),     # ==== title ====
     ('text', '', None, 'text to end or next header'))

Writing documentation
---------------------
The best way, is write documentation in PEP 257. Documentation which is gets
from pytnon elements is read with inspect.getdoc function. This function reads
element.__doc__ variable, so this variable is fill by creating comment in
element definition.

Problem could be variables. Jinja24Doc (and python documentation system) cant
set documentation for variable. But some documentation system, and jinja2doc
too have some special mechanisms how to get variable documentation. Jinja24Doc
looks for previous line of first variable definition. So you can create
one-line documentation make by comments.

.. code-block:: python

    # this is comment ehmm documentation for this nice new instance
    foo = Foo()

    # this is not documentation for foo, because this is second definition of
    # it
    foo = Goo()
