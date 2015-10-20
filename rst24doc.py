#!/usr/bin/python
"""Jinja24Doc rst2doc tool"""

from jinja24doc.main import run

description = ("Generates HTML documentation from standalone reStructuredText,"
               " python file or python module.")

run(description=description)
