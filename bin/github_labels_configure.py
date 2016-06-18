#!/usr/bin/python

"""
Add / modify all labels of all repositories
"""

import logging
from release_helper.config import get_repos, get_labels
from release_helper.labels import configure

if __name__ == '__main__':
    all_labels = get_labels()
    for repo in get_repos():
        logging.info("Configure labels of repo %s", repo.name)
        configure(repo, all_labels)
