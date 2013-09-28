== Templates ==

There are few function, which is available in jinja2 templates. First two
load_module and load_text returns documentation list.

    #!jinja
    {% set api = load_module('module') %}
    {% set sections = load_text('file.txt') %}

Other functions works with string, they format it. Function wiki generate html
string formated with base wiki syntax. It know headers, bold text, parameter
padding, code block or paragraphs defined with double newline. Except for it,
it can create links for PEP documentations and links to api definition. If you
want to create api links, you must fill api regex variable by keywords
function first.

    #!jinja
    {% set _noval = keywords(api, 'api_page.html') %}
    {{ wiki(api[0][3]) }}   {# put to document formated first documentation #}
                            {# from api (it wold be module documentation #}

Keywords function returns empty string, so you can call it from {{ }} block.
Next, keywords rewrite internal variables api regex and api link, so in this
moment, there cant do api linking for more than one page. If you have more
than one module on one page, you can join api variable from both of them.

    #!jinja
    {% set api = load_module('first_module') %}
    {% set api = api + load_module('second_module') %}
    {% set _noval = keywords(api, 'api_page.html') %}
    {{ wiki(api[0][3]) }}

There are two hidden functions, which is add to jinja2 template globals:
{truncate} and {length} as back compatibility for old jinja2 versions.

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
==== Source tarbal ====


    #!text
    Not yet

==== Source from git ====


    #!text
    ~$ git clone git://git.code.sf.net/p/poorhttp/jinja24doc jinja24doc
    or
    ~$ git clone http://git.code.sf.net/p/poorhttp/jinja24doc jinja24doc

==== Install from PyPI ====


    #!text
    Not yet

== Few words at end ==

For me, will be nice, if params padding will be do like <ul> - <li> html
lists. But jinja2doc will be create as simple way to generate documentation
easy, fast and miscellaneous. I write really fast, and as tool for generate
documentation of Poor WSGI. After this work, i put some time to document and
smooth this project, so if you want to do same improvement do it, and pleas
send me it for another users.
