#!/usr/bin/python
# encoding: utf8

import logging
from json import dump
from release_helper.config import get_repos
from release_helper.collect import collect

if __name__ == '__main__':
    all_data = {}
    all_relationships = []
    for repo in get_repos():
        logging.debug("Collecting %s", repo.name)

        data, relationships = collect(repo)

        for mst, m_data in data.items():
            all_m_data = all_data.setdefault(mst, {})
            all_m_data[repo.name] = m_data

    with open('/tmp/github-pulls.json', 'w') as f:
        dump(all_data, f, indent=4)

    with open('/tmp/github-pulls-relationships.json', 'w') as f:
        dump(all_relationships, f, indent=4)
