### gistopin

Gistopin (_gist-to-pinboard.in_) is a small python script for GitHub and [pinboard.in](http://pinboard.in) users, which automatically adds bookmarks for new Gist entries to pinboard.in account.

This allows to search easily through your gists using your favorite bookmarking service and keep a backup copy outside GitHub (if your [pinboard arching](http://pinboard.in/tour/#archive) is enabled).


## Installation

Gistopin is a python script requiring the following dependencies:

* feedparser
* configparser
* [Python-Pinboard](https://github.com/mgan59/python-pinboard)
* [TBD]

	`pip install -e git://github.com/mgan59/python-pinboard.git@v1.0#egg=python-pinboard`

All of them could be installed with `easy_install [package-name]` command.


## Usage

To run script using `config-name.py` configuration

	'''gistopin.py [config-name]'''

Also you can add it to crontab for regular execution. The following example schedules gistopin to run once each day in midnight.

	'''crontab 00 12 * * * user python /path/to/gistopin.py /path/to/gistopin-conf.py'''


## Configuration parameters

All configuration parameters should be defined in a separate file which name should be added to command line parameters during script execution.

* [TBD]
