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
    Generate and write the release
      * releases.json
      * index.html
      * burndown-%(milestone).json
    """
    releases_fn = output_filenames['releases']
    with open(releases_fn, 'w') as f:
        dump(releases, f)
        logging.info('Wrote releases data in %s', releases_fn)

    html = index(project, output_filenames['pulls'])

    index_html = output_filenames['index']
    with open(index_html, 'w') as f:
        f.write(html)
        logging.info("Wrote index %s", index_html)

    make_burndown(output_filenames['pulls'], output_filenames['burndown'])


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


def make_burndown(pulls_filename, burndown_template):
    """
    Generate the burndown-%(mst).json
    """
    logging.debug("burndown from %s JSON data", pulls_filename)
    with open(pulls_filename) as f_in:
        pulls = load(f_in)

        # No burndown data from Backlog/Legacy
        milestones = sort_milestones(pulls.keys(), add_special=False)

        for mst in milestones:
            fn = burndown_template % {'milestone': mst}

            repos = pulls[mst].keys()
            to_burn = 0
            burned = []

            for repo in repos:
                things = pulls[mst][repo]['things']
                to_burn += len(things)
                burned.extend([t['closed'] for t in things if 'closed' in t])
            burned.sort()

            burndown = {
                'to_burn': to_burn,
                'closed': [],
            }
            for closed in burned:
                to_burn -= 1
                burndown['closed'].append([closed, to_burn])

            with open(fn, 'w') as f:
                dump(burndown, f)
                logging.info('Wrote burndown data for milestone %s in %s', mst, fn)
