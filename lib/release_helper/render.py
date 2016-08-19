"""
TT rendering
"""

import glob
import logging
import os
import shutil
from datetime import datetime
from json import dump, load
from release_helper.collect import TYPE_PR, TYPE_ISSUE, BACKWARDS_INCOMPATIBLE
from release_helper.milestone import sort_milestones
from template import Template, TemplateException


# Distribute the TT files as part of the py files, unzipped
INCLUDEPATH = os.path.join(os.path.dirname(__file__), 'tt')

JAVASCRIPT = os.path.join(os.path.dirname(__file__), 'javascript')

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
    # generate the releases.json data
    releases_fn = output_filenames['releases']
    with open(releases_fn, 'w') as f:
        dump(releases, f)
        logging.info('Wrote releases data in %s', releases_fn)

    html = index(project, output_filenames['pulls'])

    index_html = output_filenames['index']
    with open(index_html, 'w') as f:
        f.write(html)
        logging.info("Wrote index %s", index_html)

    # generate the burndown json data
    make_burndown(output_filenames['pulls'], output_filenames['burndown'])

    # copy the javascript in place
    javascript_dir = output_filenames['javascript']
    for fn in glob.glob(os.path.join(JAVASCRIPT, '*.js')):
        logging.debug("copying javascript files %s to dir %s", fn, javascript_dir)
        shutil.copy(fn, javascript_dir)


def index(project, pulls_filename, previous=None, template='index'):
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

        return render(template, data)


def make_burndown(pulls_filename, burndownfn_template):
    """
    Generate the burndown-%(mst).json
    """
    logging.debug("burndown from %s JSON data", pulls_filename)
    with open(pulls_filename) as f_in:
        pulls = load(f_in)

        # No burndown data from Backlog/Legacy
        milestones = sort_milestones(pulls.keys(), add_special=False)

        for mst in milestones:
            fn = burndownfn_template % {'milestone': mst}

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

                
def make_notes(project, milestone, template, output_filenames):
    """
    Create the reelase notes file
    """
    notesfn = output_filenames['releasenotes'] % {'milestone': milestone}
    notes = release_notes(project, output_filenames['pulls'], milestone, template)
    with open(notesfn, 'w') as f:
        f.write(notes)
        logging.info("Wrote releasenotes %s", notesfn)
        

def release_notes(project, pulls_filename, milestone, template):
    """
    Generate the release notes for milestone using release template TT
    """

    logging.debug("burndown from %s JSON data", pulls_filename)

    with open(pulls_filename) as f_in:
        all_pulls = load(f_in)
        all_milestones = sort_milestones(all_pulls.keys())

        # Will fail if no current or no next milestone can be determined
        try:
            next_milestone = all_milestones[all_milestones.index(milestone)+1]
        except (IndexError, KeyError):
            logging.error("No next milestone for current %s in %s", milestone, all_milestones)
            raise

        repos = all_pulls[milestone].keys()
        repos.sort()

        # PR notes
        pulls = {}

        count_issues = 0
        count_pulls = 0
        for repo in repos:
            things = all_pulls[milestone][repo]['things']

            count_issues += len([t for t in things if t['type'] == TYPE_ISSUE])

            rpulls = [t for t in things if t['type'] == TYPE_PR]
            rpulls.sort(key=lambda t: t['title'])
            count_pulls += len(rpulls)

            pulls[repo]= rpulls

        backwards_incompatible = {}
        for repo, prs in pulls.items():
            bw_ic = [t for t in prs if t.get(BACKWARDS_INCOMPATIBLE, False)]
            if bw_ic:
                backwards_incompatible[repo] = bw_ic

        data = {
            'project': project,
            'now': datetime.utcnow().replace(microsecond=0).isoformat(' '),
            'milestone': milestone,
            'next_milestone': next_milestone,
            'count_issues': count_issues,
            'count_pulls': count_pulls,
            'pulls': pulls, # dict with repo key, and list of PRs as value
        }

        if backwards_incompatible:
            data['backwards'] = backwards_incompatible

        return render(template, data)
