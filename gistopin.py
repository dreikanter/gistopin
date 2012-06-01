#!/usr/bin/env python
# coding: utf-8

# Imports new Gist entries to pinboard.in bookmarks.
# See https://github.com/dreikanter/gistopin for details.
# Python 2.7 is required.

import feedparser
import pinboard
from argparse import ArgumentParser
from configparser import ConfigParser
from pprint import pprint, pformat
from time import mktime, sleep
from datetime import datetime
from xml.dom.minidom import parse, parseString

DEFAULT_CONF = "./gistopin.ini"
DEFAULT_CONF_SECTION = 'gistopin'
DT_FORMAT = "%Y/%m/%d %H:%M:%S"
DEBUG_MODE = True

# pinboard._debug = DEBUG_MODE


def get_config():
    parser = ArgumentParser(description="Gist to pinboard.in importer",
        epilog="""For detailed description and latest updates refer to """
        """project home page at https://github.com/dreikanter/gistopin""")

    parser.add_argument("-c", "--conf", default=DEFAULT_CONF, metavar="INI", help="configuration file (default: %s)" % DEFAULT_CONF)
    parser.add_argument("-s", "--section", default=DEFAULT_CONF_SECTION, metavar="SECTION", help="ini section (default: %s)" % DEFAULT_CONF_SECTION)
    args = parser.parse_args()

    print "Using configuration from: %s (section: %s)" % (args.conf, args.section)

    def get_params():
        conf = ConfigParser()
        with open(args.conf, 'rt') as f:
            conf.readfp(f)
        return conf.items(args.section)

    def get_tags():
        return list() if not 'tags' in result or not len(result['tags']) else [
            item.strip() for item in result['tags'].split(',')]

    def get_bool(param):
        return True if param in result and result[param].lower() in ['1', 'true'] else False

    def get_pin_pwd():
        file_prefix = 'file://'
        pwd = result['pinboard_pwd']
        if pwd.startswith(file_prefix):
            with open(pwd[len(file_prefix):]) as f:
                return f.readline().strip()
        return pwd

    try:
        result = {item[0]: item[1] for item in get_params()}

        result['tags'] = get_tags()
        result['import_private'] = get_bool('import_private')
        result['use_hashtags'] = get_bool('use_hashtags')
        result['pinboard_pwd'] = get_pin_pwd()

        return result

    except Exception, e:
        print "Error reading configuration:", e
        exit()

conf = get_config()


def get_gist_url():
    return "http://gist.github.com/%s.atom" % conf['github_user']


def extract_hashtags(text):
    """Extracts distinct hashtag collection from string"""
    return list(set([item.strip("#.,-\"\'&*^!") for item in text.split()
        if (item.startswith("#") and len(item) < 256)]))


def st2dt(st):
    return datetime.fromtimestamp(mktime(st))


def struct_time_str(st, format=DT_FORMAT):
    return st2dt(st).strftime(DT_FORMAT)


def get_gist_entities():
    """Returns latest entries from gist feed"""
    url = get_gist_url()
    print("Retrieving gists from [%s]..." % url)
    return [{'description': e.title, 'href': e.link,
        'utime': max(e.published_parsed, e.updated_parsed)}
            for e in feedparser.parse(url).entries]


def get_pinboard_entries(pinboard, fromdt):
    """Returns url:utime dictionary for specified pinboard tags"""
    print("Retrieving pinboard bookmarks from %s tagged with [%s]..." %
        (fromdt.strftime(DT_FORMAT), ", ".join(conf['tags'])))
    posts = pinboard.posts(tag=" ".join(conf['tags']), fromdt=fromdt)
    return {item['href']: item['time_parsed'] for item in posts}


def get_new_gists(gists, pins):
    new_gists = filter(lambda g: not g['href'] in pins, gists)
    updated_gists = filter(lambda g: g['href'] in pins and pins[g['href']] < g['utime'], gists)
    return new_gists, updated_gists


def post_gists():
    pnb = pinboard.PinboardAccount(conf['pinboard_user'], conf['pinboard_pwd'])
    gists = get_gist_entities()
    pins = get_pinboard_entries(pnb, st2dt(min([g['utime'] for g in gists])))
    print("Got %d existing bookmarks and %d gists." % (len(pins), len(gists)))
    new_gists, updated_gists = get_new_gists(gists, pins)
    errors_cnt = 0

    def post(gists, gists_type):
        if gists:
            print("Importing %d %s gists to pinboard..." % (len(gists), gists_type))
            for g in gists:
                print(" + %s..." % g['href'])
                # TODO: Add replace parameter to pinboard module
                # TODO: Add replace="yes" parameter to add() call
                tags = set(extract_hashtags(g['description']) + conf['tags'])
                pnb.add(g["href"], g["description"], tags=tags)

    post(new_gists, "new")
    post(updated_gists, "updated")

    print("Import succeeded." if not errors_cnt else "Import completed with %d errors." % errors_cnt)

post_gists()
