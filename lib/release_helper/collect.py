"""
Gather the relevant data for a repo, all values must be serialised.
"""

import logging
import socket
import re
from ssl import SSLError
from github import GithubException
from datetime import datetime, timedelta

MST_BACKLOG = 'Backlog'
MST_LEGACY = 'Legacy'

RE_DEPENDS = re.compile(r'((?:depends|based)\s+on|requires)\s+(?P<repository>[\w/-]*)#(?P<number>\d+)', re.IGNORECASE)


def milestones(repo):
    """
    Create milestones dict for repo
        - contains all open milestones and Backlog and Legacy
    """
    data = {}

    def add_milestone(name):
        return data.setdefault(name, {'things': [], 'closed': 0, 'open': 0, 'due': None})

    add_milestone(MST_BACKLOG)
    add_milestone(MST_LEGACY)

    for mst in repo.get_milestones(state='open'):
        mst_d = add_milestone(mst.title)
        mst_d['open'] = int(mst.open_issues)
        mst_d['closed'] = int(mst.closed_issues)

        if mst.due_on:
            mst_d['due'] = milestone.due_on.isoformat()

    return data


def process_issue(issue, msts, backlog_enddate):
    """
    Given an issue, extract any relevant data and return as dict.

    Only return issues with a milestone in msts.

    backlog_enddate is used to determine the Backlog/Legacy milestone for unassigned issues
    """

    if issue.milestone:
        milestone_name = issue.milestone.title
    elif backlog_enddate is not None:
        if issue.created_at > backlog_enddate:
            milestone_name = MST_BACKLOG
        else:
            milestone_name = MST_LEGACY

    if not milestone_name in msts:
        logging.debug("Ignoring issues")
        return {}

    this_thing = {
        'milestone': milestone_name,
        'number' : issue.number,
        'url' : issue.html_url,
        'title' : issue.title,
        'user' : issue.user.login,
        'created' :  issue.created_at.isoformat(),
        'updated' :  issue.updated_at.isoformat(),
        'state' : issue.state,
        'comment_count' : issue.comments,
        'labels' : [l.name for l in issue.labels],
        'type', 'pull-request' if issue.pull_request else 'issue',
    }

    if issue.assignee:
        this_thing['assignee'] = issue.assignee.login

    if issue.closed_at:
        this_thing['closed'] = issue.closed_at.isoformat()

    dependencies = RE_DEPENDS.search(issue.body)
    if dependencies:
        this_thing.update(dependencies.groupdict())

    return this_thing


def things(repo, msts, backlog_days=60, legacy=False):
    """
    Gather all relevant/intersting "things" from the repo .

    We care about all things that are assigned to
       one of the msts milestones
       Backlog: things from the last backlog_days days that are not assigned to a milestone
       Legacy: all the older non-assigned

    backlog_days sets the number of days in past to take into account for non-milestone isses (as Backlog milestone)
    legacy: boolean, if true, also take into account all older issues (as Legacy milestone)
    """

    if backlog_days is None:
        backlog_enddate = None
    else:
        backlog_enddate = datetime.now() - timedelta(days=backlog_days)


    if legacy:
        # Process all issues (open/close, any milestone, any date)
        all_issues = repo.get_issues()
        msts += [MST_BACKLOG, MST_LEGACY]
    else:
        mst_issues = repo.get_issues(state='all', milestone='*')
        if backlog_enddate is None:
            backlog_issues = []
        else:
            backlog_issues = repo.get_issues(milestone='none', since=backlog_enddate)
            msts.append(MST_BACKLOG)
        all_issues = chain(mst_issues, backlog_issues)

    data = dict([(m, []) for m in msts])
    relationships = []

    for issue in all_issues:
        this_thing = process_issue(isse, msts)
        if this_thing:
            mst = this_thing.pop('milestone')
            data[mst].append(this_thing)

            dep_number = this_thing.pop('dep_number', None)
            if dep_number:
                dep_repo = this_thing.pop('dep_repo') or repo.name
                relationships.append(('%s/%s' % (repo.name, this_thing['number']), 'requires', '%s/%s' % (dep_repo, dep_number)))

    return data, relationships


def retry(fn, args, kwargs, retries=3):
    """
    Retry try/except wrapper catching SSLError and socket.error
    """
    while retries:
        try:
            return fn(*args, **kwargs)
        except (SSLError, socket.error) as e:
            logging.debug("Retry %s failed (retries %s): %s", fn.__name__, retries, e)
        retries -= 1

    # This reraises with last exception
    raise Exception("No more retrials left for %s (last %s)" % (fn.__name__, e))


def collect(repo):
    """
    Gather issues (inlc PRs) for repo
    """
    data = retry(milestones, [repo], {})
    
    things_data, relations = retry(things, [repo, data.keys()], {})

    for mst, mst_data in data.items():
        mst_data['things'].extend(things_data[mst])
    
    return data, relations
