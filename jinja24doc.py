#!/usr/bin/python
"""Jinja24doc command tool for template processing """

from jinja24doc.frontend import jinja_cmdline

description = ("Generates documentation output from jinja templates.")

jinja_cmdline(description=description)
