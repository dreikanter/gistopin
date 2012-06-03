# gistopin

Gistopin (_gist-to-pinboard.in_) is a small python script for GitHub and [pinboard.in](http://pinboard.in) users, which automatically adds bookmarks for new Gist entries to pinboard.in account. This allows to search easily through created gists using your favorite bookmarking service and keep a backup copy outside GitHub (if your [pinboard arching](http://pinboard.in/tour/#archive) is enabled).

## Installation

Gistopin requiring the following modules:

* [feedparser](http://code.google.com/p/feedparser/) → 
  `pip install feedparser` or `easy_install feedparser`
* [configparser](http://docs.python.org/library/configparser.html) → 
  `pip install configparser` or `easy_install configparser`
* [Python-Pinboard](https://github.com/mgan59/python-pinboard) → 
  `pip install -e git://github.com/mgan59/python-pinboard.git@v1.0#egg=python-pinboard`

## Usage

The following command will run script using [config-name] for configuration file anme and `[section]` for configuration section (configuration is described below).

	gistopin.py -c [config-name] -s [section]

Both parameters are optional and could be omitted. In this case default configuration file (`gistopin.ini` in script directory) and configuration section (`[gistopin]`) will be used.

Gistopin could be added to crontab for regular execution. The following example schedules gistopin to run once each day in the midnight:

	crontab 00 12 * * * user python /path/to/gistopin.py /path/to/gistopin.ini


## Configuration parameters

To avoid over-complicated command line syntax, script parameters intended to be kept in configuration file with an ordinary [RFC-822](http://tools.ietf.org/html/rfc822.html) compliant syntax. As it was mentioned already default section name is `gistopin` but in could be manually specified from the command line. So single configuration file could contain multiple configurations for different pinboard or GitHub accounts.

Example:

	[gistopin]
	pinboard_user = dreikanter
	pinboard_pwd = file://../gistopin-private/pinboard-pwd.txt
	github_user = dreikanter
	shared = no
	tags = snippets, gistopin_check
	use_hashtags = yes

Parameters explanation:

* `pinboard_user` — pinboard.in user name.
* `pinboard_pwd` — pinboard.in password. Yes, this might look a bit insecure, but HTTP Basic is the only supported way to authorize on pinboard in the meantime. For better security the password could be stored in separate text file outside script configuration. In this case full path should be specified in the following way: `file://secret/path/pwd.txt`. Just in case, pinboard API calls works through HTTPS so there are a bit fewer things to worry about.
* `github_user` — Gist/GitHub user name.
* `shared` — `yes` to share new bookmarks or `no` to keep them private. Pinboard configuration overrides this parameter if new bookmarks intended to be private.
* `tags` — comma-separated list of common tags for new bookmarks. Also these tags will be used to check if the gists were imported already. Example: `snippets, gists`.
* `use_hashtags` — `yes` to extract hash tags from Gist description and use them on pinboard.

