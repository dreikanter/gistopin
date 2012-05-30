#!/usr/bin/env python

# Adds new Gist entries to users pinboard.in account.
# See https://github.com/dreikanter/gistopin

# import sys
# import os
from argparse import ArgumentParser
import ConfigParser
import feedparser
from time import mktime
import datetime
import pinboard

DEFAULT_CONF = "gistopin.ini"

HELP = """For detailed description and latest updates refer to
project home page at https://github.com/dreikanter/gistopin"""


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
    print("Retrieving gists from [%s]..." % url)
    for entry in feedparser.parse(url).entries:
        yield {
            'title': entry.title,
            'link': entry.link,
            'updated': entry.published_parsed if entry.published_parsed > entry.updated_parsed else entry.updated_parsed,
            }


def get_bookmarks(pinboard_user, pinboard_pwd, tags_list, from_dt):
    """Returns latest bookmarks from pinboard.in feed"""
    print("Retrieving pinboard bookmarks%s since %s..." %
        (((" tagged by [%s]" % ", ".join(tags_list) if len(tags_list) > 0 else "")), str(from_dt)))

    pinboad = pinboard.open(pinboard_user, pinboard_pwd)
    posts = pinboad.posts(tags_list, fromdt=from_dt)
    print(len(posts))
    exit()
    for item in posts:
        print {
            'title': item.title,
            'link': item.link,
            '*': item
            }


def get_pin_pwd(pwd):
    file_prefix = 'file://'
    if not pwd.startswith(file_prefix):
        return pwd

    try:
        f = file(pwd[len(file_prefix):])
        result = f.readline().strip()
        f.close()
    finally:
        return result


conf = get_config()
gists = get_gists(conf["github_user"])
dates = map(lambda x: x['updated'], gists)
print(datetime.time.strftime("%y/%m/%d %H:%M:%S", min(dates)))
exit()

first_gist_dt = datetime.date.today() - datetime.timedelta(1)
print(str(first_gist_dt))
exit()
bookmarks = get_bookmarks(conf['pinboard_user'], get_pin_pwd(conf['pinboard_pwd']),
    conf['common_tags'], first_gist_dt)
# description, extended, hash, href, tags, time

#for item in get_gists(conf["github_user"]):
#    print item

#get_bookmarks(conf['pinboard_user'], conf['common_tags'])
# for item in get_bookmarks(conf['pinboard_user'], conf['common_tags']):
#     print item

#TBD:
#read conf
#read gist feed, take last items
#read pinboard feed, take last items
#check if there are new/updated gists
#import new gists to pinboardin
