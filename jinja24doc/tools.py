"""Command tools entry points."""
from jinja24doc.frontend import jinja_cmdline, auto_cmdline


def jinja24doc():
    """Generates documentation output from jinja templates."""
    return jinja_cmdline(description=jinja24doc.__doc__)


def rst24doc():
    """Generates HTML documentation from standalone reStructuredText,
       python file or python module.
    """
    return auto_cmdline(description=rst24doc.__doc__,
                        file_types=('.txt', '.rst'))


def wiki24doc():
    """Generates HTML documentation from standalone wiki,
       python file or python module.
    """
    return auto_cmdline(description=wiki24doc.__doc__, formater='wiki',
                        file_types=('.txt'))
