# -*- coding: utf-8 -*-
"""
Library for reStrucuredText parsing, and generating simple HTML output.
"""

from docutils import nodes
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.frontend import OptionParser

from apidoc import linked_api

class SimpleHTMLTranslator(nodes.NodeVisitor, object):
    list_types = {'arabic': '1',
                  'loweralpha': 'a',
                  'upperalpha': 'A',
                  'lowerroman': 'i',
                  'upperroman': 'I',
                  '-': 'disc',
                  '*': 'circle',
                  '+': 'square'}
    note_symbols = ['&#x2737;', # ✷
                    '&#x2723;', # ✣
                    '&#x2729;', # ✩
                    '&#x272B;', # ✫
                    '&#x2720;', # ✠
                    '&#x273D;', # ✽
                    '&#x2744;', # ❄
                    '&#x2756;', # ❖
                    '&clubs;',  # ♣
                    '&hearts;'  # ♥
                    ]
    admonitions = ( 'attention', 'caution', 'danger', 'error', 'hint',
                    'important', 'note', 'tip', 'warning')

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.section_level = 0
        self.auto_footnote = 0
        self.used_footnote = 0
        self.auto_anonyms = 0
        self.used_anonyms = 0
        self.body = []
        self.footnotes = []
        self.citations = []
        self.hyperlinks = []
        self.substitutions = {}
        self.targets = {}
        self.references = {}

        for admonition in self.admonitions:
            self.__setattr__('visit_%s' % admonition, self.visit_admonition)
            self.__setattr__('depart_%s' % admonition, self.depart_admonition)

        for div in ('figure', 'caption', 'legend', 'topic', 'sidebar',
                    'line_block', 'line'):
            self.__setattr__('visit_%s' % div, self.visit_div)
            self.__setattr__('depart_%s' % div, self.depart_div)

        for tbl in ('field_list', 'option_list'):
            self.__setattr__('visit_%s' % tbl, self.visit_table)
            self.__setattr__('depart_%s' % tbl, self.depart_table)
        for row in ('field', 'option_list_item'):
            self.__setattr__('visit_%s' % row, self.visit_row)
            self.__setattr__('depart_%s' % row, self.depart_row)
        for col in ('field_name','field_body', 'option_group', 'description'):
            self.__setattr__('visit_%s' % col, self.visit_entry)
            self.__setattr__('depart_%s' % col, self.depart_entry)


    def output(self):
        content = self.body
        if self.footnotes or self.citations:
            content.append('<hr class="under-line">\n')
        if self.footnotes:
            content.append('<table class="footnotes">\n')
            content += self.footnotes
            content.append('</table>\n')
        if self.citations:
            content.append('<table class="citations">\n')
            content += self.citations
            content.append('</table>\n')
        retval = ''.join(content)

        for key, val in self.substitutions.items():
            retval = retval.replace(key, val)
        for key, val in self.targets.items():
            retval = retval.replace(key, val)
        return retval.strip()

    def visit_div(self, node):
        self.body.append('<div class="%s">' % node.tagname)
    def depart_div(self, node):
        self.body.append('</div>\n')

    def visit_document(self, node):
        pass
    def depart_document(self, node):
        pass

    def visit_block_quote(self, node):
        self.body.append('<blockquote>\n')

    def depart_block_quote(self, node):
        self.body.append('</blockquote>\n')

    def visit_paragraph(self, node):
        self.body.append('<p>')
    def depart_paragraph(self, node):
        self.body.append('</p>')
        if node.parent.tagname in ('field_body','entry','admonition') + self.admonitions:
            self.body.append('\n')
        elif node.parent.tagname not in \
        ('list_item', 'definition', 'footnote', 'citation'):
            self.body.append('\n\n')

    def visit_Text(self, node):
        if node.parent.tagname != 'substitution_reference':
            self.body.append(node.astext())
    def depart_Text(self, node):
        pass

    def visit_literal(self, node):
        self.body.append('<code>')
    def depart_literal(self, node):
        self.body.append('</code>')
    def visit_literal_block(self, node):
        cls = ' class="%s"' % ' '.join(node['classes']) if node['classes'] else ''
        self.body.append('<pre%s>\n' % cls)
    def depart_literal_block(self, node):
        self.body.append('\n</pre>\n')
    def visit_doctest_block(self, node):
        self.body.append('<pre>\n')
    def depart_doctest_block(self, node):
        self.body.append('\n</pre>\n')

    def visit_inline(self, node):
        classes = node.get('classes', [])
        if node.parent.tagname == 'literal_block':
            if 'keyword' in classes:
                self.body.append('<b>')
            elif 'function' in classes or 'class' in classes:
                self.body.append('<em>')
            elif 'string' in classes:
                self.body.append('<i>')
            elif 'comment' in classes:
                self.body.append('<i>')
            elif 'decorator' in classes:
                self.body.append('<var>')
            elif 'number' in classes:
                self.body.append('<u>')
            elif 'operator' in classes and 'word' in classes:
                self.body.append('<tt>')
            elif 'builtin' in classes or 'exception' in classes:
                self.body.append('<kbd>')
        else:
            cls = ' class="%s"' % ' '.join(classes) if classes else ''
            self.body.append('<span%s>' % cls)
    def depart_inline(self, node):
        if node.parent.tagname == 'literal_block':
            classes = node.get('classes', [])
            if 'keyword' in classes:
                self.body.append('</b>')
            elif 'function' in classes or 'class' in classes:
                self.body.append('</em>')
            elif 'string' in classes:
                self.body.append('</i>')
            elif 'comment' in classes:
                self.body.append('</i>')
            elif 'decorator' in classes:
                self.body.append('</var>')
            elif 'number' in classes:
                self.body.append('</u>')
            elif 'operator' in classes and 'word' in classes:
                self.body.append('</tt>')
            elif 'builtin' in classes or 'exception' in classes:
                self.body.append('</kbd>')
        else:
            self.body.append('</span>')

    def visit_bullet_list(self, node):
        self.body.append('<ul type="%s">\n' % self.list_types[node['bullet']] )
    def depart_bullet_list(self, node):
        self.body.append('</ul>\n\n')

    def visit_enumerated_list(self, node):
        self.body.append('<ol type="%s">\n' % self.list_types[node['enumtype']])
    def depart_enumerated_list(self, node):
        self.body.append('</ol>\n\n')

    def visit_list_item(self, node):
        self.body.append('<li>')
    def depart_list_item(self, node):
        self.body.append('</li>\n')

    def visit_definition_list(self, node):
        self.body.append('<dl>\n')

    def depart_definition_list(self, node):
        self.body.append('</dl>\n')

    def visit_definition_list_item(self, node):
        pass

    def depart_definition_list_item(self, node):
        pass

    def visit_footnote_reference(self, node):
        if node.get('auto', 0):
            self.used_footnote += 1
            if 'refname' in node:
                skey = '<footnote_reference refname="%s">' % node['refname']
                self.body.append('<a href="#%s"><sup>%s' % \
                                (node['refname'], skey))
                tkey = '<target refname="%s">' % node['refname']
                self.targets[tkey] = '<a href="#%s">' % node['refname']
            elif node['auto'] == '*':
                label = ''.join(self.note_symbols[int(i)] for i in str(self.used_footnote))
                self.body.append('<a href="#auto%d"><sup>%s' % \
                                (self.used_footnote, label))
            else:
                self.body.append('<a href="#auto%d"><sup>%d' % \
                                (self.used_footnote, self.used_footnote))
        else:
            self.body.append('<a href="#%s"><sup>' % node.get('refname', node.get('ids')[0]))
    def depart_footnote_reference(self, node):
        self.body.append('</sup></a>')

    def visit_footnote(self, node):
        self.context = self.body
        self.body = self.footnotes
        self.body.append('<tr>')

        if  node.get('auto', 0):    # auto
            self.auto_footnote += 1
            label = str(self.auto_footnote)
            if node['auto'] == '*':
                label = ''.join(self.note_symbols[int(i)-1] for i in label)
            if node['names']:
                name = node['names'][0]
                key = '<footnote_reference refname="%s">' % name
                self.substitutions[key] = label
            else:
                name ='auto%d' % self.auto_footnote
            self.body.append('<td><a name="%s"></a><b>[ %s ]</b></td><td>' % (name, label))
        else:
            self.body.append('<td><a name="%s"></a>' % node['names'][0])
    def depart_footnote(self, node):
        self.body.append('</td></tr>\n')
        self.body = self.context

    def visit_citation_reference(self, node):
        tkey = '<target refname="%s">' % node['refname']
        self.targets[tkey] = '<a href="#%s">' % node['refname']
        self.body.append('<a href="#%s">[' % node['refname'])
    def depart_citation_reference(self, node):
        self.body.append(']</a>')

    def visit_citation(self, node):
        self.context = self.body
        self.body = self.citations
        self.body.append('<tr>')
        self.body.append('<td><a name="%s"></a>' % node['names'][0])
    def depart_citation(self, node):
        self.body.append('</td></tr>\n')
        self.body = self.context

    def visit_label(self, node):
        if node.parent.tagname in ('footnote', 'citation'):
            self.body.append('<b>[ ')
    def depart_label(self, node):
        if node.parent.tagname in ('footnote', 'citation'):
            self.body.append(' ]</b></td><td>')

    def visit_emphasis(self, node):
        self.body.append('<em>')
    def depart_emphasis(self, node):
        self.body.append('</em>')

    def visit_strong(self, node):
        self.body.append('<b>')
    def depart_strong(self, node):
        self.body.append('</b>')

    def visit_title_reference(self, node):
        self.body.append('<cite>')
    def depart_title_reference(self, node):
        self.body.append('</cite>')

    def visit_reference(self, node):
        if node.get('anonymous', 0):
            self.auto_anonyms += 1
            ref = 'anonymous%d' % self.auto_anonyms
        else:
            ref = node.get('refname', node.get('name'))
        if 'refuri' in node:
            self.body.append('<a href="%s">' % node['refuri'])
        else:
            target = '<target refname="%s">' % ref
            self.body.append(target)
            self.references[target] = ref

    def depart_reference(self, node):
        self.body.append('</a>')

    def visit_substitution_reference(self, node):
        self.body.append('<substitution_reference refname="%s">' % node['refname'])
    def depart_substitution_reference(self, node):
        pass

    def visit_substitution_definition(self, node):
        self.context = self.body
        self.body = []
    def depart_substitution_definition (self, node):
        key = '<substitution_reference refname="%s">' % node['names'][0]
        self.substitutions[key] = ''.join(self.body)
        self.body = self.context

    def visit_target(self, node):
        if 'refuri' in node and not node.get('anonymous', 0):
            name = node['names'][0]
            ref = node.get('refuri', '#'+node.get('ids')[0])
            target = '<target refname="%s">' % name
            self.targets[target] = '<a href="%s">' % ref
            if target in self.references:
                self.hyperlinks.append('<em>%s</em>: <a href="%s">%s</a>' % \
                                        (self.references[target] ,ref, ref))
        else:
            if node.get('anonymous', 0):
                self.used_anonyms += 1
                atarget = '<target refname="anonymous%d">' % self.used_anonyms
                if 'refname' in node:
                    ntarget = '<target refname="%s">' % node['refname']
                    self.substitutions[atarget] = ntarget
                else:
                    self.targets[atarget] = '<a href="%s">' % node['refuri']
            else:
                name = node['names'][0] if node['names'] else node['refname']
                target = '<target refname="%s">' % name
                self.targets[target] = '<a href="#%s">' % name
                self.body.append('<a href="#%s">' % name)
    def depart_target(self, node):
        if not 'refuri' in node and not 'anonymous' in node:
            self.body.append('</a>')

    def visit_raw(self, node):
        if 'html' in node['format']:
            self.body.append(node.astext())
    def depart_raw(self, node):
        pass

    def visit_section(self, node):
        self.section_level += 1
        ids = node['ids'][0]
        target = '<target refname="%s">' % node['names'][0]
        self.targets[target] = '<a href="#%s">' % ids
        self.body.append('<a name="%s"></a>' % ids)
    def depart_section(self, node):
        self.section_level -= 1

    def visit_title(self, node):
        if node.parent.tagname == 'section':
            if self.section_level < 7:
                self.body.append('<h%d>' % self.section_level)
            else:
                self.body.append('<div class="h%d">' % self.section_level)
        else:
            self.body.append('<div class="title">')
    def depart_title(self, node):
        if self.section_level < 7 and node.parent.tagname == 'section':
            self.body.append('</h%d>\n' % self.section_level)
        else:
           self.body.append('</div>\n')

    def visit_subtitle(self, node):
        if node.parent.tagname == 'document':
            self.body.append('<h2>')
        else:
            self.body.append('<p class="subtitle">')
    def depart_subtitle(self, node):
        if node.parent.tagname == 'document':
            self.body.append('</h2\n>')
        else:
            self.body.append('</p>\n')

    def visit_term(self, node):
        self.body.append('<dt>')
    def depart_term(self, node):
        pass

    def visit_definition(self, node):
        self.body.append('</dt>\n')
        self.body.append('<dd>')
    def depart_definition(self, node):
        self.body.append('</dd>\n')

    def visit_system_message(self, node):
        self.body.append('<fieldset>\n')
        self.body.append('<legend>System message</legend>\n')
    def depart_system_message(self, node):
        self.body.append('</fieldset>\n\n')

    def visit_image(self, node):
        self.body.append(str(node).replace('uri', 'src').replace('<image', '<img'))
    def depart_image(self, node):
        pass

    def visit_table(self, node):
        cls = ' class="%s"' % node.tagname if node.tagname != 'table' else ''
        self.body.append('<table%s>\n' %cls)
    def depart_table(self, node):
        self.body.append('</table>\n')
    def visit_tgroup(self, node):
        pass
    def depart_tgroup(self, node):
        pass
    def visit_colspec(self, node):
        pass
    def depart_colspec(self, node):
        pass
    def visit_thead(self, node):
        self.body.append('<thead>')
    def depart_thead(self, node):
        self.body.append('</thead>\n')
    def visit_tbody(self, node):
        self.body.append('<tbody>')
    def depart_tbody(self, node):
        self.body.append('</tbody>\n')
    def visit_row(self, node):
        self.body.append('<tr>')
    def depart_row(self, node):
        self.body.append('</tr>\n')
    def visit_entry(self, node):
        colspan = ' colspan=%d' % (int(node['morecols'])+1) if 'morecols' in node else ''
        rowspan = ' rowspan=%d' % (int(node['morerows'])+1) if 'morerows' in node else ''
        if node.parent.parent.tagname == 'thead' or node.tagname == 'field_name':
            self.body.append('<th%s>' % (colspan + rowspan))
        else:
            self.body.append('<td%s>' % (colspan + rowspan))
    def depart_entry(self, node):
        if node.parent.parent.tagname == 'thead' or node.tagname == 'field_name':
            self.body.append('</th>')
        else:
            self.body.append('</td>')

    def visit_option(self, node):
        self.body.append('<code>')
    def depart_option(self, node):
        self.body.append('</code>')
    def visit_option_string(self, node):
        pass
    def depart_option_string(self, node):
        self.body.append(' ')
    def visit_option_argument(self, node):
        self.body.append('<i>')
    def depart_option_argument(self, node):
        self.body.append('</i>')

    def visit_transition(self, node):
        self.body.append('<hr>')
    def depart_transition(self, node):
        pass

    def visit_admonition(self, node):
        self.body.append('<fieldset class="%s">\n' % node.tagname)
        self.body.append('<legend>%s</legend>\n' % node.tagname.capitalize())
    def depart_admonition(self, node):
        self.body.append('</fieldset>\n\n')

    def visit_comment(self, node):
        self.body.append('<!-- ')
    def depart_comment(self, node):
        self.body.append(' -->\n')

    def visit_pending(self, node):
        raise nodes.SkipNode

    def visit_problematic(self, node):
        self.body.append('<span class="problematic">')
    def depart_problematic(self, node):
        self.body.append('</span>')


def rst(doc):
    settings = OptionParser(components=(Parser,)).get_default_values()
    parser = Parser()
    document = new_document('__doc__', settings)
    parser.parse(doc, document)

    visitor = SimpleHTMLTranslator(document)
    document.walkabout(visitor)
    out = visitor.output()

    if out.count('</p>') == 1:              # strip paragraph if is one
        out = out[out.index('>')+1:-4]

    # api links
    return linked_api(out)
