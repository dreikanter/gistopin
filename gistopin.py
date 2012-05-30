#!/usr/bin/env python

# Adds new Gist entries to users pinboard.in account.
# See https://github.com/dreikanter/gistopin

from argparse import ArgumentParser
import configparser
import feedparser

DEFAULT_CONF = "gistopin.ini"

DEFAULT_CONF_SECTION = 'gistopin'

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


def get_config():
    """Parses command line and returns configuration dictionary"""
    """or termanates the program if --h option specified."""
    parser = ArgumentParser(description="Gist to pinboard.in importer", epilog=HELP)
    parser.add_argument("-c", "--conf", default=DEFAULT_CONF, metavar="INI", help="configuration file (default: %s)" % DEFAULT_CONF)
    parser.add_argument("-s", "--section", default=DEFAULT_CONF_SECTION, metavar="SECTION", help="ini section (default: %s)" % DEFAULT_CONF_SECTION)
    args = parser.parse_args()
    print "Using configuration from: %s (section: %s)" % (args.conf, args.section)

    try:
        conf = configparser.ConfigParser()
        conf.read(args.conf)
        items = conf.items(args.section)
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


def get_gist_entities(github_user):
    """Returns latest entries from gist feed"""
    url = get_gist_url(github_user)
    print("Retrieving gists from [%s]..." % url)
    for entry in feedparser.parse(url).entries:
        yield {
            'title': entry.title,
            'link': entry.link,
            'updated': entry.published_parsed if entry.published_parsed > entry.updated_parsed else entry.updated_parsed,
            }


def get_pinboard_entities(user, tags):
    """Returns latest bookmarks from pinboard.in feed
    Args:
        user: Pinboard user name.
        tags: Tags list.
    Returns:
        List of dicts containing 'title', 'link' and 'updated' items in each item.
    """

    url = get_pinboard_url(user, tags)
    print("Retrieving pinboard bookmarks%s..." %
        ((" tagged by [%s]" % ", ".join(tags) if len(tags) > 0 else "")))
    for entry in feedparser.parse(url).entries:
        yield  {
            'title': entry['title'],
            'link': entry['link'],
            'updated': entry['updated_parsed']
            }


# def get_bookmarks(pinboard_user, pinboard_pwd, tags_list, from_st):
#     from_dt = datetime.fromtimestamp(mktime(from_st))
#     print("Retrieving pinboard bookmarks%s since %s..." %
#         (((" tagged by [%s]" % ", ".join(tags_list) if len(tags_list) > 0 else "")), str(from_dt)))

#     pinboad = pinboard.open(pinboard_user, pinboard_pwd)
#     posts = pinboad.posts(tags_list)
#     print(len(posts))
#     exit()
#     for item in posts:
#         print {
#             'title': item.title,
#             'link': item.link,
#             '*': item
#             }


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


def get_new_gists(github_user, pinboard_user, tags):
    gists = get_gist_entities(github_user)
    pins = get_pinboard_entities(pinboard_user, tags)

    if not len(gists) or not len(pins):
        return gists

    pinsd = {}
    for pin in pins:
        pinsd[pin['link']] = pin

    result = []
    for gist in gists:
        if not gist['link'] in pinsd or pinsd[gist['link']]['updated'] < gist['updated']:
            result.append(gist)
    return result


conf = get_config()
new_gists = get_new_gists(conf["github_user"], conf['pinboard_user'], conf['tags'])
if not len(new_gists):
    print("No new gists found.")

#TBD:
#check if there are new/updated gists (updated > max(updated) from pins)
#import new gists to pinboardin

# "%Y/%m/%d %H:%M:%S"
