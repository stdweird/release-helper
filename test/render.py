import release_helper.render
import os
from release_helper.render import render

# Monkey path the inlcude path for testing
release_helper.render.INCLUDEPATH = os.path.join(os.path.dirname(__file__), 'tt')

import unittest

class UtilsTest(unittest.TestCase):
    def test_render(self):
        """
        Test simple rendering example
        """
        txt = render('hello', {'world': 'trivial test'})
        self.assertEqual(txt, "Hello trivial test.\n", msg="Trivial test result: %s" % txt)
