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


def get_hashtags(text, order=False):
    tags = set([item.strip("#.,-\"\'&*^!") for item in text.split() if (item.startswith("#") and len(item) < 256)])
    return sorted(tags) if order else tags


def format_datetime(struct_time):
    return datetime.fromtimestamp(mktime(struct_time))


def read_gist_feed(github_user):
    url = "http://gist.github.com/%s.atom" % github_user
    d = feedparser.parse(url)
    print "Feed title:", d.feed.title
    print "Link:", d.feed.link

    if hasattr(d.feed, 'subtitle'):
        print "Subtitle:", d.feed.subtitle

    print "Updated:", d.feed.updated
    print "Updated (parsed):", format_datetime(d.feed.updated_parsed)
    print "Feed ID:", d.feed.id
    print "\nEntries:"

    for entry in d.entries:
        print " * Title:", entry.title
        print "   Link: %s", entry.link
        print "   Published: %s", format_datetime(entry.published_parsed)
        print "   Updated: %s", format_datetime(entry.updated_parsed)
        print "   Summary length:", len(entry.summary)
        print "   Content items count:", len(entry.content)


def get_config():
    parser = ArgumentParser(description="Gist to pinboard.in importer", epilog=HELP)
    parser.add_argument("-c", "--conf", default=DEFAULT_CONF, metavar="INI",
         help="configuration file (default: %s)" % DEFAULT_CONF)
    args = parser.parse_args()
    print "Using configuration from:", args.conf

    try:
        conf = ConfigParser.ConfigParser()
        conf.read(args.conf)
        return conf.items("gistopin")

    except Exception, e:
        print "Error reading configuration:", e
        exit()

conf = get_config()
print conf

#TBD:
#read conf
#read gist feed, take last items
#read pinboard feed, take last items
#check if there are new/updated gists
#import new gists to pinboardin
