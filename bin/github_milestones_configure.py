#!/usr/bin/python

import logging
from release_helper.config import get_repos
from release_helper.milestone import generate_milestones, configure

if __name__ == '__main__':
    milestones = generate_milestones()
    for repo in get_repos():
        logging.info("Configure milestones of repo %s", repo.name)
        configure(repo, milestones)
