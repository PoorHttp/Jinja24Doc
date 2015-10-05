#!/bin/sh

mkdir -p out
ln -sf ../../templates/blue.css out/style.css
#PYTHONPATH=./:./jinja24doc
#( python ../jinja24doc.py test_wiki.html ../template > out/test_wiki.html )
( python ../jinja24doc.py test_module_wiki.html ../templates > out/test_module_wiki.html )
( python ../jinja24doc.py test_module_wiki_linked.html ../templates > out/test_module_wiki_linked.html )
#( python ../jinja24doc.py test_rst.html ../template > out/test_rst.html )
( python ../jinja24doc.py test_module_rst.html ../templates > out/test_module_rst.html )
( python ../jinja24doc.py test_module_rst_linked.html ../templates > out/test_module_rst_linked.html )
