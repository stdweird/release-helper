"""
Retrieve configuration information
"""

import logging
from github import Github

# TODO: Get following vars in  a more decent way
USERNAME = None
OAUTH_TOKEN = None
ORGANISATION = None
REPOS = None
STANDARD_LABELS = []

from github_release_config import *

g = Github(USERNAME, OAUTH_TOKEN)
q = g.get_user(ORGANISATION)


def get_repos():
    """
    Return list of Repository instances
    """
    repos = []
    for r in REPOS:
        print r
        repos.append(q.get_repo(r))

    logging.info("Using %s repositories: %s", len(repos), [r.name for r in repos])

    return repos

def get_labels():
    """
    Return the labels map: name => hexcolor
    """
    # Requires the dictionary STANDARD_LABELS = { label: hexcolor } to be defined in github_release_config
    return STANDARD_LABELS
