#!/usr/bin/python

from jinja24doc.frontend import auto_cmdline

description = ("Generates HTML documentation from standalone reStructuredText,"
               " python file or python module.")

auto_cmdline(description=description, file_types=('.txt', '.rst'))
