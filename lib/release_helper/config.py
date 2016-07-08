"""
Retrieve configuration information
"""

import ConfigParser
import logging
import os
import re
from github import Github

DEFAULT_CONFIG_FILES = ['/etc/release_helper.cfg', os.path.expanduser('~/.release_helper.cfg')]

# Section names
MAIN = 'main' # is optional, github section is than default github-api section
LABELS = 'labels'

# main attributes + default github section name
GITHUB = 'github' # comma seperated list of section names with github-api details

# github attrbutes
USERNAME = 'username' # username MANDATORY
TOKEN = 'token' # auth token for username MANDATORY
API = 'api' # non-default API (e.g. for github enterprise)
ORGANISATION = 'organisation' # github organisation(/user) to use to query repos MANDATORY
WHITE = 'white' # white filter on repo names (comma separated list of regex; no exact match)
BLACK = 'black' # black filter on repo names (comma separated list of regex; no exact match)

# Config key
REPOS = 'repos'

# Config state, set/updated by make_config
CONFIG = {
    REPOS: [],
    LABELS: {},
}


def read_config(cfgs=None):
    """
    Read the config from config files cfgs (or use DEFAULT_CONFIG_FILES if None)
    """
    if cfgs is None:
        cfgs = DEFAULT_CONFIG_FILES

    config = ConfigParser.ConfigParser()
    config.read(cfgs)

    return config


def make_config(cfgs=None):
    """
    Parse the config files and populate the CONFIG dict
    """
    config = read_config(cfgs=cfgs)

    if config.has_option(MAIN, GITHUB):
        githubs = map(str.strip, config.get(MAIN, GITHUB).split(','))
    else:
        githubs = [GITHUB]
    logging.debug("Using githubs sections %s", githubs)
    for gh in githubs:
        if config.has_section(gh):
            opts = dict(config.items(gh))

            try:
                kwargs = {
                    'login_or_token': opts[USERNAME],
                    'password': opts[TOKEN],
                }
            except KeyError:
                logging.error('%s and/or %s are mandatory for each github section', USERNAME, TOKEN)
                raise

            if API in opts:
                kwargs['base_url'] = opts[API]

            g = Github(**kwargs)

            if ORGANISATION in opts:
                q = g.get_user(ORGANISATION)
            else:
                msg = 'Missing %s in github section %s' % (ORGANISATION, gh)
                logging.error(msg)
                raise Exception(msg)

            # Apply white filter
            if WHITE in opts:
                white = map(re.compile, map(str.strip, config.get(gh, WHITE).split(',')))
            else:
                white = None

            # Apply black filter
            if BLACK in opts:
                black = map(re.compile, map(str.strip, config.get(gh, BLACK).split(',')))
            else:
                black = None

            # Get all repo names
            for repo in q.get_repos():
                if white and not any(map(re.search, white, [repo.title]*len(white))):
                    # if white and no match, skip
                    continue
                if black and any(map(re.search, black, [repo.title]*len(black))):
                    # if black and match skip
                    continue
                CONFIG[REPOS].append(repo)
        else:
            msg = "No github section %s found" % gh
            logging.error(msg)
            raise Exception(msg)

    # Labels from labels section
    if config.has_section(LABELS):
        CONFIG[LABELS].update(dict(config.items(LABELS)))
    else:
        logging.warning("No %s section found" % LABELS)

    # For unittesting mainly
    return CONFIG


def get_repos():
    """
    Return list of Repository instances
    """
    repos = CONFIG[REPOS]

    logging.info("Using %s repositories: %s", len(repos), [r.name for r in repos])

    return repos


def get_labels():
    """
    Return the labels map: name => hexcolor
    """
    labels = CONFIG[LABELS]

    logging.info("Using %s labels: %s", len(labels), ','.join(["%s=%s" % (k,v) for k,v in labels.items()]))

    return labels
