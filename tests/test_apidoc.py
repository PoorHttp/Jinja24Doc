from jinja24doc.apidoc import load_module, keywords

def test_load_module():
    load_module('sys')

def test_keywords():
    api = load_module('sys')
    keywords(api)
