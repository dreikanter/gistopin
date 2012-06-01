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
import requests
from requests.auth import HTTPBasicAuth
from xml.dom.minidom import parse, parseString
import pinboard

DEFAULT_CONF = "./gistopin.ini"
DEFAULT_CONF_SECTION = 'gistopin'
PINBOARD_API_URL = "https://api.pinboard.in/v1/%s"
DEBUG_MODE = True
DEBUG_PIN_FEED_URL = "http://localhost/gistopin/pinboard.rss.txt"
DEBUG_GIST_FEED_URL = "http://localhost/gistopin/gist.atom.txt"
PINBOARD_MIN_REQ_INTERVAL = 3000


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

        def get_bool(conf, param):
            return True if param in conf and conf[param].lower() in ['1', 'true'] else False

        result['import_private'] = get_bool(result, 'import_private')
        result['use_hashtags'] = get_bool(result, 'use_hashtags')

        file_prefix = 'file://'
        if result['pinboard_pwd'].startswith(file_prefix):
            with open(result['pinboard_pwd'][len(file_prefix):]) as f:
                result['pinboard_pwd'] = f.readline().strip()

        return result

    except Exception, e:
        print "Error reading configuration:", e
        exit()


conf = get_config()


def get_gist_url():
    return DEBUG_GIST_FEED_URL if DEBUG_MODE else (
        "http://gist.github.com/%s.atom" % conf['github_user'])


# def get_pinboard_url(username, tags):
#     return DEBUG_PIN_FEED_URL if DEBUG_MODE else "http://feeds.pinboard.in/rss/u:%s/%s" % (username, '/'.join(["t:" + item for item in tags]))


# def get_pinapi_url(method):
#     return PINBOARD_API_URL % method


def extract_hashtags(text):
    """Extracts distinct hashtag collection from string"""
    tags = set([item.strip("#.,-\"\'&*^!") for item in text.split()
        if (item.startswith("#") and len(item) < 256)])
    return tags


def struct_time_str(st, format="%Y/%m/%d %H:%M:%S"):
    return datetime.fromtimestamp(mktime(st)).strftime(format)


# def file_exists(file_name):
#     if os.path.isfile(file_name):
#         try:
#             open(file_name)
#             return True
#         except:
#             pass
#     return False


def get_gist_entities():
    """Returns latest entries from gist feed"""
    url = get_gist_url()
    print("Retrieving gists from [%s]..." % url)
    return [{'description': e.title, 'href': e.link,
        'utime': max(e.published_parsed, e.updated_parsed)}
            for e in feedparser.parse(url).entries]


# def get_pinboard_entities(user, tags):
#     """Returns latest bookmarks from pinboard.in feed
#     Args:
#         user: Pinboard user name.
#         tags: Tags list.
#     Returns:
#         List of dicts containing 'tile', 'link' and 'updated' items in each item.conf['github_user']#     """

    # url = get_pinboard_url(user, tags)
    # print("Retrieving pinboard bookmarks%s..." % ((" tagged by %s" %
#         ", ".join(map(lambda t: "#" + t, tags)) if len(tags) > 0 else "")))
#     return [{'title': e.title, 'link': e.link, 'updated': e.updated_parsed}
#         for e in feedparser.parse(url).entries]


# TODO: Limit date/time with the oldes gist utime
def get_pinboard_entries(pinboard):
    """Returns url:utime dictionary for specified pinboard tags"""
    print("Retrieving pinboard posts tagged with [%s]..." % ", ".join(conf['tags']))
    return {item['href']: struct_time_str(item['time_parsed']) for item in pinboard.posts(tag=" ".join(conf['tags']))}


# def get_new_gists(github_user, pinboard_user, tags):
#     gists = get_gist_entities(github_user)
#     # Note: Set comprehensions (added in python 2.7) causes SublimeLinter to display syntax error
#     pins = {e['link']: e['updated'] for e in get_pinboard_entities(pinboard_user, tags)}
#     print("Got %d existing bookmarks and %d gists" % (len(pins), len(gists)))
#     return filter(lambda g: not g['link'] in pins, gists), filter(lambda g: g['link'] in pins and pins[g['link']] < g['updated'], gists)


def get_new_gists(gists, pins):
    new_gists = filter(lambda g: not g['href'] in pins, gists)
    updated_gists = filter(lambda g: g['href'] in pins and pins[g['href']] < g['utime'], gists)
    return new_gists, updated_gists


def post_gists():
    pnb = pinboard.PinboardAccount(conf['pinboard_user'], conf['pinboard_pwd'])
    gists = get_gist_entities()
    pins = get_pinboard_entries(pnb)
    print("Got %d existing bookmarks and %d gists" % (len(pins), len(gists)))
    gists = get_new_gists(gists, pins)
    print("Importing %d gists to pinboard..." % len(gists))
    errors_cnt = 0
    for gist in gists:
        # gist_tags=conf['tags']+extract_hashtags(gist['description'])
        # pnb.add(gists["url"], gists["description"], tags=gist_tags, replace="yes")
        pprint(gists)

    print("Import succeeded." if not errors_cnt else "Import completed with %d errors." % errors_cnt)

# def yesno(value):
#     return "yes" if value else "no"


# def pin_request(user, pwd, method, params):
#     """Performs GET request to Pinboard API"""

#     r = requests.get(get_pinapi_url(method), auth=HTTPBasicAuth(user, pwd), params=params)

#     if DEBUG_MODE:
#         print "Performed GET request:", r.url
#         print "Status:", r.status_code
#         print("\n\n")
#         pprint(r)

#     return r


# def add_bookmark(url, description, tags, shared, user, pwd):
#     """Adds new (or ovewrite existing) bookmark to pinboard.in"""

#     r = pin_request(user, pwd, "posts/add", params={
#         "url": url.strip(),
#         "description": description.strip(),
#         "tags": " ".join(filter(bool, [t.strip() for t in tags])),
#         "replace": yesno(True),
#         "shared": yesno(shared),
#         "toread": yesno(False),
#     })

#     return True


post_gists()

#   u'description': u'PHP Filters',
#   u'extended': u'',
#   u'hash': u'dcebb38dcc214853b9d91b531365eac8',
#   u'href': u'http://www.owasp.org/software/labs/phpfilters.html',
#   u'tags': [u'php', u'webdev', u'snippets'],
#   u'time': u'2005-07-06T06:52:30Z',
#   u'time_parsed': time.struct_time(tm_year=2005, tm_mon=7, tm_mday=6, tm_hour=6, tm_min=52, tm_sec=30, tm_wday=2, tm_yday=187, tm_isdst=-1)}]

# add_bookmark("http://microsoft.com", "Microsoft Corp.", ['companies', 'microsoft'],
#     False, conf['pinboard_user'], get_pin_pwd(conf['pinboard_pwd']))
# exit()

# new_gists, updated_gists = get_new_gists(conf["github_user"], conf['pinboard_user'], conf['tags'])

# print("\n\nnew_gists")
# pprint(new_gists)

# print("\n\nupdated_gists")
# pprint(updated_gists)
