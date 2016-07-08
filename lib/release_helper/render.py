"""
TT rendering
"""

import logging
import os
from datetime import datetime
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
        logging.error(msg)
        raise TemplateException('render', msg)


def index(prev):
    """
    Generate index.html from index.tt
    """
    data = {
        'now': datetime.utcnow().replace(microsecond=0).isoformat(' '),
        'milestones': '', # milestones
        'previous_releases': dict([(x, 1) for x in prev]), # dict for easy lookup
        'data': {}, # dict with milestone key, and dict value, which has repo key
    }
    return render('index', data)
