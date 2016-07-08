#!/usr/bin/python
# encoding: utf8

import argparse
import logging
from json import dump
from release_helper.config import get_repos
from release_helper.collect import collect

GH_PULLS = '/tmp/github-pulls.json'
GH_PULLS_RELATIONS = '/tmp/github-pulls-relationships.json'

def get_args():
    """
    Build up and parse commandline
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="set debug loglevel", action="store_true")

    parser.add_argument("-c", "--collect", help="collect github repository information", action="store_true")

    args = parser.parse_args()
    return args

def collect_all():
    """
    collect github repository information
    """
    all_data = {}
    all_relations = []
    for repo in get_repos():
        logging.debug("Collecting %s", repo.name)

        data, relations = collect(repo)

        for mst, m_data in data.items():
            all_m_data = all_data.setdefault(mst, {})
            all_m_data[repo.name] = m_data

        all_relations.extend(relations)

    with open(GH_PULLS, 'w') as f:
        dump(all_data, f, indent=4)
        logging.debug('Collect wrote data in %s', GH_PULLS)

    with open(GH_PULLS_RELATIONS, 'w') as f:
        dump(all_relations, f, indent=4)
        logging.debug('Collect wrote relation data in %s', GH_PULLS_RELATIONS)

if __name__ == '__main__':
    logger = logging.getLogger()
    lvl = logging.INFO

    args = get_args()
    if args.debug:
        lvl = logging.DEBUG
    logger.setLevel(lvl)

    logging.debug('Release helper start')
    if args.collect:
        logging.info('Collect')
        collect_all()

    logging.debug('Release helper end')
