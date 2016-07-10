#!/usr/bin/env python

import glob
from setuptools import setup


SETUP = {
    'name': 'release-helper',
    'version': '0.1.0',
    'author': 'James Adams',
    'author_email': 'james.adams@stfc.ac.uk',
    'license': 'APL',
    'packages' : ['release_helper'],
    'package_dir': {'': 'lib'},
    'scripts': glob.glob('bin/*.py') + glob.glob('bin/*.sh'),
    'install_requires': [
        'PyGithub',
        'Template-Python', # python TT port
        # For tests
        #'mock',
        #'prospector',
    ],
    'test_suite': 'test',
    'data_files': [
        # Look for better location
        ('release_helper/data', glob.glob('data/*html') + glob.glob('data/*example') + glob.glob('data/*/js')),
        ('release_helper/tt', glob.glob('lib/release_helper/tt/*.tt')),
        ('release_helper/javascript', glob.glob('lib/release_helper/javascript/*.js')),
    ],
    'zip_safe': False, # shipped TT files
}

if __name__ == '__main__':
    setup(**SETUP)
