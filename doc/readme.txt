== What is Jinja24Doc ==

Jinja24doc is lightweight documentation generator for python modules with
jinja2 templates. It is part of *Poor Http* group tools (WSGI connector,
WSGI/HTTP Server and mod_python connector). It could load modules and gets
documentation for its items. No configuration is needed, only jinja2
templates. Your or from jinja2doc package.

It is more *powerful pydoc*, with style what you want. You can format
your documentation string with some simple chars like in *AsciiDoc* and *Wiki*,
and *highlight* your examples code. And of course it create automatic links to
*PEP*.

== Manual in few seconds ==
Just create your {template.html} file, and add to them these lines:

    #!jinja
    {% set title = 'Your Python Module' %}
    {% set api = load_module('your_python_module') %}
    {% include '_reference.html' %}

and call the jinja24doc tool with right parameters from path where your
python module is available:

    #!text
    ~$ jinja24doc template.html ./:/usr/local/share/jinja24doc/templates/ > page.html
    ~$ cp /usr/local/share/jinja24doc/templates/blue.css ./style.css

If you want to import modules from your package, which are not installed on
system, or which are not in actual directory, you must set PYTHONPATH
environment variable. Next example extend module search path to ./falias,
./morias and ./poorwsgi directories:

    #!text
    ~$ PYTHONPATH=falias:morias:poorwsgi \
        jinja24doc template.html ./:/usr/local/share/jinja24doc/templates/ > page.html
    ~$ cp /usr/local/share/jinja24doc/templates/inverse.css ./style.css


jinja24doc program parameters:

    #!text
    jinja24doc [-v] template [path[:path]]

    -v          - verbose mode
    template    - file, which will be read as jinja2 template
    path        - jinja2 template path or paths separates by colons

== Templates ==

There are few function, which is available in jinja2 templates. First two
load_module and load_text returns documentation list.

    #!jinja
    {% set api = load_module('module') %}
    {% set sections = load_text('file.txt') %}

Other functions works with string, they format it. Function wiki generate html
string formated with base wiki syntax. It know headers, bold text, parameter
padding, code block or paragraphs defined with double newline. Except for it,
it can create links for PEP documentations and links to api definition. If
you want to create api links, you must fill api regex variable by keywords
function first.

    #!jinja
    {% do keywords(api, 'api_page.html') %}
    {{ wiki(api[0][3]) }}   {# put to document formated first documentation #}
                            {# from api (it wold be module documentation #}

Keywords function returns empty string, so you can call it from {{ }} block.
Next, keywords rewrite internal variables api regex and api link, so in this
moment, there cant do api linking for more than one page. If you have more
than one module on one page, you can join api variable from both of them.

    #!jinja
    {% set api = load_module('first_module') %}
    {% set api = api + load_module('second_module') %}
    {% do keywords(api, 'api_page.html') %}
    {{ wiki(api[0][3]) }}

There are two hidden functions, which is add to jinja2 template globals:
{truncate} and {length} as back compatibility for old jinja2 versions.

=== Public templates ===
There are some public templates, which you find in
{share/jinja24doc/templates} directory. All of them need set up *title*
variable and *api* variable. But they use another variables For more detail
see to code of template which you can use. Variables could be:
    title       - html page title
    api         - list of tuples - api data. See Data structure in manual.
    sections    - variable looks like api, but generate from load_text.
    description - html page description
    author      - html page author

Public templates which you can use are:
==== _simple.html ====
Simple html web page. Style is included.

==== _simple_with_submodules.html ====
Simple html web page. Style is included. All submodules are included
recursive. This could be demo, how you can generate manual from your code
recursively.

==== _reference.html ====
This template generates html pages looks like Jinja24Doc manual. There are
some different styles: {red.css, blue.css, green.css, gray.css and
inverse.css} which you can use with this template. You must only copy to
output directory as style.css ;)

==== _text.html ====
This template looks like {_reference.html}, but it is prepare to generate html
page from text. This template needs *sections* variable instead of api. It
looks like api, but contain data generate from text file. See to load_text
function.

Like reference.html template, this use styles too, so You must only copy to
output directory as style.css too.

== Data structure ==

The documentation list which returns functions load_module and load_text
looks like that:

    ((type, name, args, documentation),)    # all values are strings

Of course, some items don't have all values, so on their place is None or
another value, typical for their type. Next list is typical for load_module
function.

    (('module', 'name', None, documentation),
     ('submodule', 'name', None, ''),   # submodule don't have documentation
     ('class', 'ClassName', None, documentation),
     ('method', 'ClassName.name', args, documentation)),
     ('function', 'name', args, documentation),
     ('variable', 'name', value, ''))   # variable have value instead of arguments
                                        # and can't have documentation yet

For load_text function is this typical list:

    (('h1', 'title', None, ''),     # = title =
     ('h2', 'title', None, ''),     # == title ==
     ('h3', 'title', None, ''),     # === title ===
     ('h4', 'title', None, ''),     # ==== title ====
     ('text', '', None, 'text to end or next header'))

== Writing documentation ==

The best way, is write documentation as is nice readable with pydoc or another
python native tools. Documentation which is gets from pytnon elements is read
with inspect.getdoc function. This function reads element.__doc__ variable, so
this variable is fill by creating comment in element definition.

    """
        This could be nice documentation for all python module.
    """

    def boo():
        """ This is one line documentation """

    class Foo:
        """ This is more line documentation 
            of this nice class.
        """

    class Goo:
        """
        This is another way of more line documentation
        of this nice class.
        """

Problem could be variables. Jinja24Doc (and python documentation system) cant
set documentation for variable. But some documentation system, and jinja2doc
too have some special mechanisms how to get variable documentation. Jinja24Doc
looks for previous line of first variable definition. So you can create
one-line documentation make by comments.

    # this is comment ehmm documentation for this nice new instance
    foo = Foo()

    # this is not documentation for foo, because this is second definition of
    # it
    foo = Goo()

== Get jinja2doc ==
==== Source tarball ====


    #!text
    ~$ wget http://sourceforge.net/projects/poorhttp/files/jinja24doc-1.0.1.tar.gz/download
    ~$ tar xzf jinja24doc-1.0.1.tar.gz
    ~$ cd jinja24doc-1.0.1
    ~$ python setup.py install

==== Source from git ====


    #!text
    ~$ git clone git://git.code.sf.net/p/poorhttp/jinja24doc jinja24doc
    or
    ~$ git clone http://git.code.sf.net/p/poorhttp/jinja24doc jinja24doc
    
    ~$ cd jinja24doc
    ~$ python setup.py install

==== Install from PyPI ====


    #!text
    ~$ pip install jinja24doc

== Few words at end ==

For me, will be nice, if params padding will be do like <ul> - <li> html
lists. But jinja2doc will be create as simple way to generate documentation
easy, fast and miscellaneous. I write really fast, and as tool for generate
documentation of Poor WSGI. After this work, i put some time to document and
smooth this project, so if you want to do same improvement do it, and pleas
send me it for another users via sf.net or to mail: mcbig at zeropage.cz.

=== Python 3 ===

Jinja24doc works with python 3 well, but be carefully with generation
documentation for both python versions (2 and 3). Some modules, classes,
functions, methods and variables of course are different. So compiled regular
expressions from re module has different flag number by default for example.
