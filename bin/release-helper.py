#!/usr/bin/python
# encoding: utf8

import argparse
import logging
from release_helper.config import make_config, get_repos, get_json_filenames
from release_helper.collect import collect

def get_args():
    """
    Build up and parse commandline
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="set debug loglevel", action="store_true")
    parser.add_argument("-C", "--configs", help="comma-separated list of config files")

    parser.add_argument("-c", "--collect", help="collect github repository information", action="store_true")

    args = parser.parse_args()
    return args


def main():
    logger = logging.getLogger()
    lvl = logging.INFO

    args = get_args()
    if args.debug:
        lvl = logging.DEBUG

    logger.setLevel(lvl)

    cfgs = None
    if args.configs:
        cfgs = args.configs.split(',')

    make_config(cfgs=cfgs)

    repos = get_repos()
    json_filenames = get_json_filenames()

    logging.debug('Release helper start')
    if args.collect:
        logging.info('Collect')
        collect(repos, json_filenames)

    logging.debug('Release helper end')

if __name__ == '__main__':
    main()
