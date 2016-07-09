"""
TT rendering
"""

import logging
import os
from datetime import datetime
from json import dump, load
from release_helper.milestone import sort_milestones
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


def make_html(project, releases, output_filenames):
    """
    Generate and write the release index.html
    """
    html = index(project, output_filenames['pulls'])

    releases_fn = output_filenames['releases']
    with open(releases_fn, 'w') as f:
        dump(releases, f, indent=4)
        logging.info('Wrote releases data in %s', releases_fn)

    index_html = output_filenames['index']
    with open(index_html, 'w') as f:
        f.write(html)
        logging.info("Wrote index %s", index_html)


def index(project, pulls_filename, previous=None):
    """
    Generate index.html from index.tt

    Load data from pulls_filename json
    """
    if previous is None:
        previous = []

    logging.debug("index from %s JSON data", pulls_filename)
    with open(pulls_filename) as f_in:
        pulls = load(f_in)

        milestones = sort_milestones(pulls.keys())

        data = {
            'project': project,
            'now': datetime.utcnow().replace(microsecond=0).isoformat(' '),
            'milestones': previous + milestones, # milestones
            'previous_releases': dict([(x, 1) for x in previous]), # dict for easy lookup
            'data': pulls, # dict with milestone key, and dict value, which has repo key
        }

        return render('index', data)
