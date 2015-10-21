#!/usr/bin/python
"""Jinja24Doc wiki24doc tool"""

from jinja24doc.wiki import wiki
from jinja24doc.main import auto_cmdline

description = ("Generates HTML documentation from standalone wiki,"
               " python file or python module.")

auto_cmdline(description=description, formater=wiki)
