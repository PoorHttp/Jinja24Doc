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
    {% wiki(api[0][3]) %}

There are two hidden functions, which is add to jinja2 template globals:
{truncate} and {lenght} as back compatibility for old jinja2 versions.

== Writing documentation ==

The best way, is write documentation as is nice readable with pydoc or another
python native tools. Documentation which is gets from pytnon elements is read
with inspect.getdoc function. This function reads element.__doc__ variable, so
this variable is fill by creating comment in element definition.


== Get jinja2doc ==
==== Source tarbal ====


    #!text
    Not yet

==== Source from git ====


    #!text
    ~$ git clone git://git.code.sf.net/p/poorhttp/git poorhttp-git
    or
    ~$ git clone http://git.code.sf.net/p/poorhttp/git poorhttp-git

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
