# gistopin

Gistopin (acronym from _gist-to-pinboard.in_) is a small python script for GitHub and [pinboard.in](http://pinboard.in) users, which automatically adds bookmarks for new Gist entries to pinboard.in account. This allows to search easily through created gists using your favorite bookmarking service and keep a backup copy outside GitHub (if your [pinboard arching](http://pinboard.in/tour/#archive) is enabled).

## Installation

Gistopin requires the following modules:

* [feedparser](http://code.google.com/p/feedparser/) → 
  `pip install feedparser` or `easy_install feedparser`
* [configparser](http://docs.python.org/library/configparser.html) → 
  `pip install configparser` or `easy_install configparser`
* [Python-Pinboard](https://github.com/mgan59/python-pinboard) → 
  `pip install -e git://github.com/mgan59/python-pinboard.git@v1.0#egg=python-pinboard`

## Usage

Import process parameters should be specified in configuration file (see _Configuration_ section below). By default script will use `[gistopin]` section of `gistopin.ini` located in the same directory as `gistopin.py`. But the configuration file and section names could be specified manually through the command line options:

	gistopin.py -c [config-name] -s [section]

Both parameters are optional and could be omitted. As usual `-h` or `--help` will display command line help.

Gistopin could be added to crontab for regular execution. The following example schedules it to run once each day in the midnight:

	crontab 00 12 * * * user python /path/to/gistopin.py -c /path/to/gistopin.ini


## Configuration

To avoid over-complicated command line syntax, script parameters intended to be kept in configuration file with an ordinary [RFC-822](http://tools.ietf.org/html/rfc822.html) compliant syntax. As it was mentioned already default section name is `gistopin` but a single configuration file could multiple sections for different pinboard or GitHub accounts.

Here is an example:

	[gistopin]
	pinboard_user = dreikanter
	pinboard_pwd = file://$secretplace/pinboard.txt
	github_user = dreikanter
	shared = no
	tags = snippets, gistopin_check
	use_hashtags = yes

Parameters explanation:

* `pinboard_user` — pinboard.in user name.
* `pinboard_pwd` — pinboard.in password. Yes, this might look a bit insecure, but HTTP Basic is the only supported way to authorize on pinboard in the meantime. For better security the password could be stored in a separate text file outside script configuration. In this case path should be specified in the following way: `file://secret/place/pwd.txt` (environment variables could be used in both %windows% or $unix styles).
* `github_user` — Gist/GitHub user name.
* `shared` — `yes` to share new bookmarks or `no` to keep them private. Pinboard configuration overrides this parameter if new bookmarks intended to be private.
* `tags` — comma-separated list of common tags for new bookmarks. Also these tags will be used to check if the gists were imported already. Example: `snippets, gists`.
* `use_hashtags` — `yes` to extract hash tags from Gist description and use them on pinboard.


## FAQ

**Q:** Why the import is so slow?  
**A:** Pinboard API has a limitation for 3 second intervals between requests. And each bookmark import is a separate request.
