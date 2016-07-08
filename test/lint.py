from prospector.run import Prospector
from prospector.config import ProspectorConfig
import os
import pprint
import re
import sys
import unittest

class UtilsTest(unittest.TestCase):
    # List of regexps patterns applied to code or message of a prospector.message.Message
    #   Blacklist: if match, skip message, do not check whitelist
    #   Whitelist: if match, fail test
    PROSPECTOR_BLACKLIST = [
    ]
    PROSPECTOR_WHITELIST = [
        'undefined',
        'no-value-for-parameter',
        'dangerous-default-value',
        'redefined-builtin',
        'bare-except',
        'E713',  # not 'c' in d: -> 'c' not in d:
        'arguments-differ',
        'unused-argument',
        'unused-variable',
        'reimported',
        'F811', # redefinition of unused name
        'unused-import',
        'syntax-error',
    ]

    # Prospector commandline options (positional path is added automatically)
    PROSPECTOR_OPTIONS = [
        '--strictness', 'medium',
        '--max-line-length', '120',
        '--absolute-paths',
    ]

    def test_prospector(self):

        if os.environ.get('NO_PROSPECTOR', '0') in ('1', 'y', 'yes'):
            self.assertTrue(True, msg='Skipping prospector test')
            return

        sys.argv = ['release-helper-prospector']

        # extra options needed
        sys.argv.extend(self.PROSPECTOR_OPTIONS)
        # add/set repository path as basepath
        sys.argv.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        config = ProspectorConfig()
        prospector = Prospector(config)

        prospector.execute()

        blacklist = map(re.compile, self.PROSPECTOR_BLACKLIST)
        whitelist = map(re.compile, self.PROSPECTOR_WHITELIST)

        failures = []
        for msg in prospector.get_messages():
            # example msg.as_dict():
            #  {'source': 'pylint', 'message': 'Missing function docstring', 'code': 'missing-docstring',
            #   'location': {'function': 'TestHeaders.test_check_header.lgpl', 'path': u'headers.py',
            #                'line': 122, 'character': 8, 'module': 'headers'}}

            if any([bool(reg.search(msg.code) or reg.search(msg.message)) for reg in blacklist]):
                continue

            if any([bool(reg.search(msg.code) or reg.search(msg.message)) for reg in whitelist]):
                failures.append(msg.as_dict())

        self.assertFalse(failures, "prospector failures: %s" % pprint.pformat(failures))

if __name__ == '__main__':
    unittest.main()
