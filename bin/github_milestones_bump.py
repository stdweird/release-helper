#!/usr/bin/python

import logging
from release_helper.config import get_repos
from release_helper.milestone import bump

if __name__ == '__main__':
    for repo in get_repos():
        logging.info("Bump milestones of repo %s with 2 months", repo.name)
        bump(repo, months=2)
