import datetime
import os
import unittest
import release_helper.render
from release_helper.render import render, index
from mock import patch

ORIG_INCLUDE = release_helper.render.INCLUDEPATH

class UtilsTest(unittest.TestCase):
    def test_render(self):
        """
        Test simple rendering example
        """

        # Monkey patch the inlcude path for testing
        release_helper.render.INCLUDEPATH = os.path.join(os.path.dirname(__file__), 'tt')

        txt = render('hello', {'world': 'trivial test'})

        # restore it
        release_helper.render.INCLUDEPATH = ORIG_INCLUDE

        self.assertEqual(txt, "Hello trivial test.\n", msg="Trivial test result: %s" % txt)


    @patch('release_helper.render.datetime')
    def test_index(self, mocked_datetime):
        """
        Test rendering index using TT
        """
        mocked_datetime.utcnow.return_value=datetime.datetime(1970, 1, 2, 3, 4, 5, 6)
        
        self.maxDiff = None
        self.longMessage = True

        fn = os.path.join(os.path.dirname(__file__), 'data', 'index.html')
        res = open(fn).read()

        data = {
        }

        self.assertMultiLineEqual(index(data), res)
