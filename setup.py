#!/usr/bin/env python

from setuptools import setup, find_packages
import gistopin

setup(
    name=gistopin.__name__,
    description=gistopin.__doc__,
    version=gistopin.__version__,
    license=gistopin.__license__,
    author=gistopin.__author__,
    author_email=gistopin.__email__,
    url=gistopin.__url__,
    long_description=open('README.md').read(),
    platforms=['any'],
    packages=find_packages(),
    py_modules=['gistopin'],
    entry_points={'console_scripts': ['gistopin = gistopin:main']},
    include_package_data=True,
    zip_safe=False,
    scripts=['gistopin.py'],
    requires=['feedparser', 'configparser', 'pinboard'],
    classifiers=[
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python',
       'Programming Language :: Python :: 2.7',
       # TODO: Test and add other versions
    ],
    dependency_links=[
        'https://github.com/mgan59/python-pinboard/tarball/master#egg=pinboard'
    ],
)
