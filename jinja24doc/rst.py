
"""
Library for reStrucuredText parsing, and generating simple HTML output.
"""

from docutils.core import publish_parts
from docutils_tinyhtml import Writer

from sys import version_info
if version_info[0] == 2:
    from io import open

import os

from jinja24doc.apidoc import ApiDoc, pep_rfc
from jinja24doc.wiki import re_source, re_python, _python


def _doctest_code(obj):
    tmp = obj.groups()
    if tmp[0] == 'doctest':
        source = re_python.sub(_python, tmp[1])
    else:
        source = tmp[1]
    return '<pre class="%s">%s</pre>' % (tmp[0], source)


class Rst(ApiDoc):
    """Class based on ApiDoc."""

    def rst(self, doc, link='link', top='top', title='__doc__',
            section_level=2, system_message=False):
        """
        Call reStructuredText docutil parser for doc and return it with html
        representation of reStructuredText formating. For more details see
        http://docutils.sourceforge.net/rst.html.
        """
        writer = Writer()
        parts = publish_parts(source=doc,
                              writer=writer,
                              writer_name='html',
                              settings_overrides={
                                  'link': link, 'top': top, 'title': title,
                                  'initial_header_level': section_level,
                                  'no_system_messages': not system_message})

        out = parts['body'] + parts['html_line'] + \
            parts['html_footnotes'] + parts['html_citations']

        out = re_source.sub(_doctest_code, out.strip())

        if out.startswith('<p') and out.endswith('</p>') and \
                out.count('</p>') == 1:     # strip paragraph if is one
            out = out[out.index('>')+1:-4]
        return self.linked_api(pep_rfc(out))

    def load_rst(self, rstfile, link='link', top='top', system_message=False):
        """Load reStructuredText file and create docs list of headers and text.

        Parameters:
            rstfile - string, reStructured source file name (readme.rst)
            link - link label for headers. If is empty, link href will be
                hidden.
            top - top label for headers. If is empty, top href will be hidden.

            #!jinja
            {% set sections = load_rst('readme.rst', '', '') %}
            {% type, filename, _none_, text = sections[-1] %}
        """

        x_rstfile = ''
        for path in self.paths:
            if os.access(path+'/'+rstfile, os.R_OK):
                x_rstfile = path+'/'+rstfile
                break
        if not x_rstfile:
            raise SystemExit('Access denied to text file %s' % rstfile)

        with open(x_rstfile, 'r', encoding=self.encoding) as f:
            doc = f.read()

        writer = Writer()
        parts = publish_parts(source=doc,
                              source_path=x_rstfile,
                              writer=writer,
                              writer_name='html',
                              settings_overrides={
                                  'link': link, 'top': top,
                                  'no_system_messages': not system_message})

        out = parts['body']
        if parts['html_footnotes'] or parts['html_citations']:
            out += parts['html_line'] + \
                parts['html_footnotes'] + parts['html_citations']

        out = re_source.sub(_doctest_code, out)

        if out.startswith('<p') and out.endswith('</p>') and \
                out.count('</p>') == 1:     # strip paragraph if is one
            out = out[out.index('>')+1:-4]

        out = self.linked_api(pep_rfc(out))

        retval = list(('h%d' % lvl, self.uni(name), id, '')
                      for lvl, name, id in parts['sections'])
        # TODO: append '(author, date, verstion)' from rst if exist like in
        # module
        retval.append(('text', parts['title'], None, self.uni(out)))
        return retval
# endclass
