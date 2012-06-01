#!/usr/bin/env python
# coding: utf-8

# Adds new Gist entries to users pinboard.in account.
# See https://github.com/dreikanter/gistopin

import os
from argparse import ArgumentParser
from configparser import ConfigParser
import feedparser
from pprint import pprint, pformat
import codecs
from time import mktime
from datetime import datetime

DEFAULT_CONF = "./gistopin.ini"
DEFAULT_CONF_SECTION = 'gistopin'
PINBOARD_API_URL = "https://%s:%s@api.pinboard.in/"
DEBUG_MODE = True
DEBUG_PIN_FEED_URL = "http://localhost/gistopin/pinboard.rss.txt"
DEBUG_GIST_FEED_URL = "http://localhost/gistopin/gist.atom.txt"


def get_gist_url(username):
    return DEBUG_GIST_FEED_URL if DEBUG_MODE else ("http://gist.github.com/%s.atom" % username)


def get_pinboard_url(username, tags):
    return DEBUG_PIN_FEED_URL if DEBUG_MODE else "http://feeds.pinboard.in/rss/u:%s/%s" % (username, '/'.join(["t:" + item for item in tags]))


def get_hashtags(text, order=False):
    """Extracts distinct hashtag collection from string"""
    tags = set([item.strip("#.,-\"\'&*^!") for item in text.split()
        if (item.startswith("#") and len(item) < 256)])
    return sorted(tags) if order else tags


def struct_time_str(st, format="%Y/%m/%d %H:%M:%S"):
    return datetime.fromtimestamp(mktime(st))


def file_exists(file_name):
    if os.path.isfile(file_name):
        try:
            open(file_name)
        except:
            return False
    return True


def get_config():
    """Parses command line and returns configuration dictionary"""
    """or termanates the program if --h option specified."""

    parser = ArgumentParser(description="Gist to pinboard.in importer",
        epilog="""For detailed description and latest updates refer to """
            """project home page at https://github.com/dreikanter/gistopin""")
    parser.add_argument("-c", "--conf", default=DEFAULT_CONF, metavar="INI", help="configuration file (default: %s)" % DEFAULT_CONF)
    parser.add_argument("-s", "--section", default=DEFAULT_CONF_SECTION, metavar="SECTION", help="ini section (default: %s)" % DEFAULT_CONF_SECTION)
    args = parser.parse_args()
    print "Using configuration from: %s (section: %s)" % (args.conf, args.section)

    try:
        conf = ConfigParser()
        with open(args.conf, 'rt') as f:
            conf.readfp(f)

        result = dict()

        for item in conf.items(args.section):
            result[item[0]] = item[1]

        if not 'tags' in result or not result['tags']:
            result['tags'] = list()
        else:
            result['tags'] = list(set([item.strip() for item in result['tags'].split(',')]))

        result['import_private'] = get_bool_param(result, 'import_private')
        result['use_hashtags'] = get_bool_param(result, 'use_hashtags')

        return result

    except Exception, e:
        print "Error reading configuration:", e
        exit()


def get_bool_param(conf_dict, param):
    return True if param in conf_dict and conf_dict[param].lower() in ['1', 'true'] else False


def get_gist_entities(github_user):
    """Returns latest entries from gist feed"""
    url = get_gist_url(github_user)
    print("Retrieving gists from [%s]..." % url)
    return [{'title': e.title, 'link': e.link, 'updated': max(e.published_parsed, e.updated_parsed)}
        for e in feedparser.parse(url).entries]


def get_pinboard_entities(user, tags):
    """Returns latest bookmarks from pinboard.in feed
    Args:
        user: Pinboard user name.
        tags: Tags list.
    Returns:
        List of dicts containing 'title', 'link' and 'updated' items in each item.
    """

    url = get_pinboard_url(user, tags)
    print("Retrieving pinboard bookmarks%s..." % ((" tagged by %s" %
        ", ".join(map(lambda t: "#" + t, tags)) if len(tags) > 0 else "")))
    return [{'title': e.title, 'link': e.link, 'updated': e.updated_parsed}
        for e in feedparser.parse(url).entries]


def get_pin_pwd(pwd):
    file_prefix = 'file://'

    if not pwd.startswith(file_prefix):
        return pwd

    with open(pwd[len(file_prefix):]) as f:
        return f.readline().strip()


def get_new_gists(github_user, pinboard_user, tags):
    gists = get_gist_entities(github_user)
    # Note: Set comprehensions (added in python 2.7) causes SublimeLinter to display syntax error
    pins = {e['link']: e['updated'] for e in get_pinboard_entities(pinboard_user, tags)}
    print("Got %d existing bookmarks and %d gists" % (len(pins), len(gists)))
    return filter(lambda g: not g['link'] in pins, gists), filter(lambda g: g['link'] in pins and pins[g['link']] < g['updated'], gists)


conf = get_config()
new_gists, updated_gists = get_new_gists(conf["github_user"], conf['pinboard_user'], conf['tags'])

print("\n\nnew_gists")
pprint(new_gists)

print("\n\nupdated_gists")
pprint(updated_gists)

#TBD:
#import new gists to pinboardin
