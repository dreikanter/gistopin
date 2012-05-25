#!/usr/bin/env python

# Adds new Gist entries to users pinboard.in account.
# See https://github.com/dreikanter/gistopin

# import sys
# import os
from argparse import ArgumentParser
import ConfigParser
import feedparser
from time import mktime
from datetime import datetime

DEFAULT_CONF = "gistopin.ini"

HELP = """For detailed description and latest updates refer to
project home page at https://github.com/dreikanter/gistopin"""

VERBOSE = False


def trace(message):
    if VERBOSE:
        print message


def get_gist_url(username):
    return "http://gist.github.com/%s.atom" % username


def get_pinboard_url(username, tags):
    return "http://feeds.pinboard.in/rss/u:%s/%s" % (username, '/'.join(["t:" + item for item in tags]))


def get_hashtags(text, order=False):
    """Extracts distinct hashtag collection from string"""
    tags = set([item.strip("#.,-\"\'&*^!") for item in text.split()
        if (item.startswith("#") and len(item) < 256)])
    return sorted(tags) if order else tags


def format_datetime(struct_time):
    return datetime.fromtimestamp(mktime(struct_time))


def get_config():
    """Parses command line and returns configuration dictionary"""
    """or termanates the program if --h option specified."""
    parser = ArgumentParser(description="Gist to pinboard.in importer", epilog=HELP)
    parser.add_argument("-c", "--conf", default=DEFAULT_CONF, metavar="INI", help="configuration file (default: %s)" % DEFAULT_CONF)
    args = parser.parse_args()
    print "Using configuration from:", args.conf

    try:
        conf = ConfigParser.ConfigParser()
        conf.read(args.conf)
        items = conf.items('gistopin')
        result = dict()

        for item in items:
            result[item[0]] = item[1]
        if not 'common_tags' in result or not result['common_tags']:
            result['common_tags'] = list()
        else:
            result['common_tags'] = list(set([item.strip() for item in result['common_tags'].split(',')]))

        result['verbose'] = get_bool_param(result, 'verbose')
        result['import_private'] = get_bool_param(result, 'import_private')
        result['use_hashtags'] = get_bool_param(result, 'use_hashtags')

        return result

    except Exception, e:
        print "Error reading configuration:", e
        exit()


def get_bool_param(conf_dict, param):
    return True if param in conf_dict and conf_dict[param].lower() in ['1', 'true'] else False


def get_gists(github_user):
    """Returns latest entries from gist feed"""
    url = get_gist_url(github_user)
    trace("Retrieving gists from [%s]..." % url)
    for entry in feedparser.parse(url).entries:
        yield {
            'title': entry.title,
            'link': entry.link,
            'updated': entry.published_parsed if entry.published_parsed > entry.updated_parsed else entry.updated_parsed,
            }


def get_bookmarks(pinboard_user, tags):
    """Returns latest bookmarks from pinboard.in feed"""
    url = get_pinboard_url(pinboard_user, tags)
    trace("Retrieving gists from [%s]..." % url)

    items = feedparser.parse(get_pinboard_url(pinboard_user, tags))['items']
    for item in items:
        yield {
            'title': item.title,
            'link': item.link,
            '*': item
            }

conf = get_config()
VERBOSE = conf['verbose']

#for item in get_gists(conf["github_user"]):
#    print item

for item in get_bookmarks(conf['pinboard_user'], conf['common_tags']):
    print item

#TBD:
#read conf
#read gist feed, take last items
#read pinboard feed, take last items
#check if there are new/updated gists
#import new gists to pinboardin
