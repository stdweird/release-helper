"""
Retrieve configuration information
"""

import ConfigParser
import logging
import os
import tempfile
import re
from github import Github

DEFAULT_CONFIG_FILES = ['/etc/release_helper.cfg', os.path.expanduser('~/.release_helper.cfg')]

# Section names
MAIN = 'main' # is optional, github section is than default github-api section
LABELS = 'labels'
RELEASES = 'releases'

# main attributes + default github section name
GITHUB = 'github' # comma seperated list of section names with github-api details
PROJECT = 'project' # project name, unique name used to store e.g. the json files

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
    PROJECT: 'project',
    REPOS: [],
    LABELS: {},
    RELEASES: {},
}

def read_config(cfgs):
    """
    Read the config from config files cfgs (or use DEFAULT_CONFIG_FILES if None)
    """
    config = ConfigParser.ConfigParser()

    read_cfgs = config.read(cfgs)
    if len(cfgs) != len(read_cfgs):
        logging.warn("Not all cfgs %s were found: %s", cfgs, read_cfgs)

    return config


def make_config(cfgs=None, use_github=True):
    """
    Parse the config files and populate the CONFIG dict
    """
    if cfgs is None:
        cfgs = DEFAULT_CONFIG_FILES

    logging.debug("Reading config from configfiles: %s", cfgs)
    config = read_config(cfgs=cfgs)

    if config.has_option(MAIN, PROJECT):
        CONFIG[PROJECT] = config.get(MAIN, PROJECT)

    if not use_github:
        githubs = []
    elif config.has_option(MAIN, GITHUB):
        githubs = map(str.strip, config.get(MAIN, GITHUB).split(','))
    else:
        githubs = [GITHUB]

    total = 0

    logging.debug("Using githubs sections %s (use_github %s)", githubs, use_github)
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
                q = g.get_organization(opts[ORGANISATION])
                logging.debug("%s %s in github section %s", ORGANISATION, opts[ORGANISATION], gh)
            else:
                logging.debug('Missing %s in github section %s, using current user %s', ORGANISATION, gh, kwargs['login_or_token'])
                q = g.get_user()

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
                total += 1
                if white and not any(map(re.search, white, [repo.name]*len(white))):
                    # if white and no match, skip
                    logging.debug("Skipped repo %s in github %s due to white %s", repo.name, gh, [x.pattern for x in white])
                    continue
                if black and any(map(re.search, black, [repo.name]*len(black))):
                    # if black and match skip
                    logging.debug("Skipped repo %s in github %s due to black %s", repo.name, gh, [x.pattern for x in black])
                    continue

                logging.debug("Adding repo %s in github %s", repo.name, gh)
                CONFIG[REPOS].append(repo)
        else:
            msg = "No github section %s found" % gh
            logging.error(msg)
            raise Exception(msg)

    logging.debug("Got %s repos out of %s total: %s", len(CONFIG[REPOS]), total, [x.name for x in CONFIG[REPOS]])

    # Labels from labels section
    if config.has_section(LABELS):
        CONFIG[LABELS].update(dict(config.items(LABELS)))
    else:
        logging.warning("No %s section found" % LABELS)

    # Releases section
    # milestone=start,rcs,target
    if config.has_section(RELEASES):
        for mst, dates in config.items(RELEASES):
            CONFIG[RELEASES][mst] = dict(zip(['start', 'rcs', 'target'], dates.split(',')[:3]))
    else:
        logging.warning("No %s section found" % RELEASES)

    # For unittesting mainly
    return CONFIG

def get_project():
    """
    Return project name
    """
    project = CONFIG[PROJECT]

    logging.info("Project names %s", project)

    return project


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


def get_releases():
    """
    Return the labels map: name => hexcolor
    """
    releases = CONFIG[RELEASES]

    logging.info("Using %s releases: %s", len(releases), ','.join(sorted(releases.keys())))

    return releases


def get_output_filenames():
    """
    Return the basedir and (abspath) output filenames (e.g. JSON, html)
    """
    tmpdir = tempfile.gettempdir()
    basedir = os.path.join(tmpdir, CONFIG[PROJECT])

    names = {
        'pulls': os.path.join(basedir, 'pulls.json'),
        'relations': os.path.join(basedir, 'relations.json'),
        'index': os.path.join(basedir, 'index.html'),
        'releases': os.path.join(basedir, 'releases.json'),
        'burndown': os.path.join(basedir, 'burndown-%(milestone)s.json'), # filename template
        'javascript': basedir, # directory
    }

    return basedir, names
