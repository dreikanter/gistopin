#!/usr/bin/env python

from distutils.core import setup

setup(name='gistopin',
    version='0.0.1',
    author='Alex Musayev',
    author_email='alex.musayev@gmail.com',
    url='https://github.com/dreikanter/gistopin',
    description='Python script to bookmark new Gist entries with pinboard.in service',
    long_description=open('README.md').read(),
    scripts=['gistopin.py'],
    license="BSD",
    requires=['feedparser', 'configparser'],
    py_modules=['pinboard'],
    data_files=[('config', ['gistopin.ini'])],)
