from jinja24doc.apidoc import ApiDoc


def test_load_module():
    api = ApiDoc()
    api.load_module('sys')


def test_keywords():
    api = ApiDoc()
    module = api.load_module('sys')
    api.keywords(module)


def test_typing():
    api = ApiDoc()
    api.load_module('typing')


def test_self():
    api = ApiDoc()
    api.load_module('jinja24doc.apidoc')
