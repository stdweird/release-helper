"""
TT rendering
"""

import logging
import os
from template import Template, TemplateException

# Distribute the TT files as part of the py files, unzipped
INCLUDEPATH = os.path.join(os.path.dirname(__file__), 'tt')

def render(tt, data):
    """
    Given tt filename, render using data

    (.tt suffix is added if missing)
    """
    opts = {
        'INCLUDE_PATH': [INCLUDEPATH],
    }

    if not tt.endswith('.tt'):
        tt += '.tt'
    
    try:
        t = Template(opts)
        return t.process(tt, data)
    except TemplateException as e:
        msg = "Failed to render TT %s with data %s (TT opts %s): %s" % (tt, data, opts, e)
        logging.exception(msg)
        raise TemplateException(msg)
