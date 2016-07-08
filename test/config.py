import os
import unittest
import release_helper.config as cfg


# mock.patch really isn't made for this
class Repo(object):
    def __init__(self, name):
        self.name = name

class GHU(object):
    def __init__(self, org, ghargs):
        self.org = org
        self.ghargs = ghargs

    def get_repos(self):
        if self.ghargs.get('base_url', None) is None:
            ts = ['repoxyz', 'repoabc']
        else:
            ts = ['repopublic', 'reposecret']
        return map(Repo, ts)

GHCALLED = []
class GH(object):
    def __init__(self, **kwargs):
        GHCALLED.append(kwargs)

    def get_user(self, user):
        return GHU(user, GHCALLED[-1])

    def get_organization(self, org):
        return GHU(org, GHCALLED[-1])


# monkey patch Github
cfg.Github = GH

class UtilsTest(unittest.TestCase):

    def setUp(self):
        global GHCALLED
        GHCALLED = []

    def test_make_config(self):

        fn = os.path.join(os.path.dirname(__file__), 'data', 'test1.cfg')

        config = cfg.make_config([fn])

        self.assertEqual(GHCALLED, [{'login_or_token': 'example1', 'password': '1234567890'},
                                    {'password': 'abcdef123456', 'login_or_token': 'localuser', 'base_url': 'https://enterprise.example.com/some/subtree/v3/'}])
        self.assertEqual(sorted(config.keys()), ['labels', 'project', 'repos'])
        self.assertEqual(config['project'], 'mytest')
        self.assertEqual(config['labels'], {'bug': 'ef2929', 'question': '123456'})
        self.assertEqual([r.name for r in config['repos']], ['repoabc', 'repopublic'])
