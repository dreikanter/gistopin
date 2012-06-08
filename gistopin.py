#!/usr/bin/env python

"""Python script to bookmark new Gist entries with pinboard.in service"""

from os.path import expandvars
from argparse import ArgumentParser
from datetime import datetime
from time import mktime, sleep
from xml.dom.minidom import parse, parseString
from configparser import ConfigParser
import feedparser
import pinboard

__author__ = "Alex Musayev"
__email__ = "alex.musayev@gmail.com"
__copyright__ = "Copyright 2012, %s <http://alex.musayev.com>" % __author__
__license__ = "BSD"
__version_info__ = (1, 0, 0)
__version__ = ".".join(map(str, __version_info__))
__url__ = "http://github.com/dreikanter/gistopin"

# Enables super-verbose output for pinboard.in API interaction:
# pinboard._debug = True

DT_FORMAT = "%Y/%m/%d %H:%M:%S"
DEFAULT_TAGS = "gist, snippets"
GIST_FEED_URL = "http://gist.github.com/%s.atom"


# Script configuration ========================================================

def get_config():
    def get_args():
        parser = ArgumentParser(description="Gist to pinboard.in importer, Version %s" % __version__,
            epilog="""For detailed description and latest updates refer tothe project home page at %s""" % __url__)

        parser.add_argument("-c", "--conf", metavar="INI", help="configuration file")
        parser.add_argument("-s", "--section", default=None, metavar="SECTION",
            help="ini section (default is the first one)")
        parser.add_argument("-d", "--dry", action='store_true',
            help="dry run (download gists but do not bookmark anything)")
        args = parser.parse_args()

        if not args.conf:
            goodbye("Configuration file not specified.", 1)

        return args

    def get_params(conf_file, section):
        print("Using configuration from: %s (section: %s)" % (conf_file, section if section else "default"))

        parser = ConfigParser()
        with open(conf_file, 'rt') as f:
            parser.readfp(f)

        if section and not section in parser.sections():
            raise Exception("%s not found" % (("section [%s]" % section) if section else "first section"))

        try:
            section = section if section else parser.sections()[0]
            return {item[0]: item[1] for item in parser.items(section)}
        except:
            raise Exception(("section [%s] not found" % section) if section else "no sections defined")

    def validate(params):
        mandatory_params = ['pinboard_user', 'pinboard_pwd', 'github_user']
        insfprm = filter(lambda x: not x in params, [item for item in mandatory_params])
        if insfprm:
            goodbye("Insuffifient parameters: [%s]" % ", ".join(insfprm))
        return params

    def purify(params, dry):
        def split_tags(tags):
            return filter(lambda x: x, [item.strip() for item in tags.split(',')])

        def parse_bool(value):
            return True if str(value).lower() in ['1', 'true', 'yes', 'y'] else False

        def get_pwd(pwd):
            file_prefix = 'file://'
            if pwd.startswith(file_prefix):
                with open(expandvars(pwd[len(file_prefix):])) as f:
                    return f.readline().strip()
            return pwd

        params = params or {}
        params.update({
            'pinboard_pwd': get_pwd(params.get('pinboard_pwd', '')),
            'tags': split_tags(params.get('tags', DEFAULT_TAGS)),
            'shared': parse_bool(params.get('shared', True)),
            'use_hashtags': parse_bool(params.get('use_hashtags', True)),
            'dry': dry,
        })

        return params

    try:
        args = get_args()
        return purify(validate(get_params(args.conf, args.section)), args.dry)
    except Exception, e:
        goodbye("Error reading configuration: %s" % str(e), 2, False)


# Service interaction =========================================================

def get_gist_entities(github_user):
    """Returns latest entries from gist feed"""
    url = GIST_FEED_URL % github_user
    print("Retrieving gists from [%s]..." % url)
    return [{'description': e.title, 'href': e.link,
        'utime': max(e.published_parsed, e.updated_parsed)}
            for e in feedparser.parse(url).entries]


def get_pinboard_entries(pinboard, tags, fromdt):
    """Returns url:utime dictionary for specified pinboard tags"""
    print("Retrieving pinboard bookmarks from %s tagged with [%s]..." %
        (fromdt.strftime(DT_FORMAT), ", ".join(tags)))
    posts = pinboard.posts(tag=" ".join(tags), fromdt=fromdt)
    return {item['href']: item['time_parsed'] for item in posts}


def get_new_gists(gists, pins):
    new_gists = filter(lambda g: not g['href'] in pins, gists)
    updated_gists = filter(lambda g: g['href'] in pins and pins[g['href']] < g['utime'], gists)
    return new_gists, updated_gists


# Common helpers ==============================================================

def goodbye(message="", exit_code=0, short_help=True):
    """A bit extended die() with more optimistic name."""
    if message:
        print(message)
    if short_help:
        print("Use -h for command line help.")
    exit(exit_code)


def extract_hashtags(text, tags_to_append=[]):
    """Extracts distinct sorted hashtag collection from a string, complemented with tags_to_append items."""
    return sorted(set([item.strip("#.,-\"\'&*^!") for item in text.split()
        if (item.startswith("#") and len(item) < 256)] + tags_to_append))


def st2dt(st):
    """Converts struct_time to datetime."""
    return datetime.fromtimestamp(mktime(st))


def yesno(value):
    """Converts logic value to 'yes' or 'no' string."""
    return "yes" if value else "no"


# =============================================================================

def main():
    conf = get_config()
    if conf['dry']:
        print("Dry run")
    pin = pinboard.PinboardAccount(conf['pinboard_user'], conf['pinboard_pwd'])
    gists = get_gist_entities(conf['github_user'])
    pins = get_pinboard_entries(pin, conf['tags'], st2dt(min([g['utime'] for g in gists])))
    print("Got %d existing bookmarks and %d gists." % (len(pins), len(gists)))
    new_gists, updated_gists = get_new_gists(gists, pins)
    errors_cnt = 0

    def post(gists, gists_type):
        if gists:
            print("Importing %d %s gists to pinboard..." % (len(gists), gists_type))
            for g in gists:
                print(" + %s..." % g['href'])
                tags = " ".join(extract_hashtags(g['description'], conf['tags']))
                if not conf['dry']:
                    pin.add(g["href"], g["description"], tags=tags, replace=yesno(True), shared=yesno(conf['shared']))

    post(new_gists, "new")
    post(updated_gists, "updated")

    print("Import succeeded." if not errors_cnt else "Import completed with %d errors." % errors_cnt)

if __name__ == '__main__':
    main()
