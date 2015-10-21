#!/usr/bin/python
"""Jinja24Doc rst2doc command tool"""

from jinja24doc.main import auto_cmdline

description = ("Generates HTML documentation from standalone reStructuredText,"
               " python file or python module.")

auto_cmdline(description=description)
