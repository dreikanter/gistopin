#!/usr/bin/env python

import sys
from distutils.core import setup
import gistopin

scripts = ['gistopin.py']
if sys.platform == 'win32':
    scripts.append('gistopin.bat')

setup(
    name=gistopin.__name__,
    description=gistopin.__doc__,
    version=gistopin.__version__,
    license=gistopin.__license__,
    author=gistopin.__author__,
    author_email=gistopin.__email__,
    url=gistopin.__url__,
    long_description=open('README.md').read(),
    scripts=scripts,
    platforms=['any'],
    requires=['feedparser', 'configparser', 'pinboard'],
)
