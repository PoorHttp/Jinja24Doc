unicode_exist = True

try:
    unicode()
except:
    unicode_exist = False

def uni(text):
    """ Function always return unicode or str in Python 3.x """
    if unicode_exist and isinstance(text, str):
        return text.decode('utf-8')
    return text
