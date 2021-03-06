#!/usr/bin/python
# encoding: utf8

HEADER = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Quattor Backlog</title>
    <link rel="stylesheet" type="text/css" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/octicons/2.0.2/octicons.css">
    <style type="text/css">
      @import url(http://fonts.googleapis.com/css?family=Lato:400);
      body {
        padding-bottom: 40px;
        font-family: 'Lato', 'Helvetica', sans-serif;
        background-color: #eef1f1;
      }
      h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
        font-family: 'Lato', 'Helvetica', sans-serif;
      }
      blockquote {
        font-size: small;
      }
      .navbar-inverse {
        background-color: #004080;
      }
      .navbar-inverse .navbar-brand {
        color: white;
      }
      .text-github-open {
        color: #6cc644;
      }
      .text-github-closed {
        color: #6E5494;
      }
      .thing-closed {
        display: none;
        opacity: 0.75;
      }
    </style>
    <script src="http://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/2.8.3/moment.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/moment-timezone/0.2.2/moment-timezone.min.js"></script>
  </head>
  <body>
    <div class="navbar navbar-inverse navbar-static-top" role="navigation">
      <div class="container">
        <a class="navbar-brand"><img src="/img/quattor_logo_navbar.png" width="94" height="23" alt="quattor logo"> &mdash; Releasing</a>
        <ul class="nav navbar-nav">
          <li class="active"><a href="/release/">Backlog</a></li>
          <li><a href="/release/burndown.html">Burndown</a></li>
        </ul>
      </div>
    </div>
'''

FOOTER = '''
  <script type="text/javascript">
    $(function() {
      $('.reldate').each(function(index) {
        $(this).text(moment.tz($(this).text(), "YYYY-MM-DDTHH:mm:ss", "UTC").fromNow());
      });
    });
  </script>
  </body>
</html>
'''

OUTFILE = 'index.html'


from json import load
from cgi import escape
from datetime import datetime


# Render data
with open('/tmp/github-pulls.json') as f_in:
    data = load(f_in)

    # Hacky numerical sort for our release numerbing scheme
    milestones = data.keys()
    milestones = [[int(i) for i in m.split('.')] for m in milestones if m != 'Unassigned']
    milestones.sort()
    milestones = [u'.'.join(map(str,m)) for m in milestones] + ['Unassigned']
    print milestones


    with open(OUTFILE, 'w') as f:
        f.write(HEADER)

        f.write('<div class="container">\n')
        f.write('''<button class="btn btn-default btn-sm pull-right" onclick="$('.thing-closed').toggle('slow')">Show/Hide Closed Items</button>\n''')

        f.write('<ul class="nav nav-tabs" role="tablist">\n')
        for milestone in milestones:
            f.write('<li><a href="#%s" role="tab" data-toggle="tab">%s</a></li>\n' % (milestone.replace('.', '-'), milestone))
        f.write('</ul>\n')

        f.write('<div class="tab-content">\n')
        f.write('<div class="tab-pane active">\n')
        f.write('<div class="panel panel-default">\n')
        f.write('<div class="panel-body">\n')
        f.write('<p><span class="glyphicon glyphicon-arrow-up"></span> Select a release to view backlog</p>\n')
        f.write('</div>\n')
        f.write('</div>\n')
        f.write('</div>\n')

        for milestone in milestones:
            i_progress = 0
            i_closed = 0
            i_open = 0
            m_due = 'never'

            print "    %s" % (milestone)
            style = 'default'
            if milestone == 'Unassigned':
                style = 'danger'
            repos = data[milestone].keys()
            repos.sort()
            f.write('<div class="tab-pane panel panel-%s" id="%s">\n' % (style, milestone.replace('.', '-')))
            f.write('<table class="table panel-body">\n')

            for repo in repos:
                i_closed += data[milestone][repo]['closed']
                i_open += data[milestone][repo]['open']

                print "        " + repo
                r = data[milestone][repo]
                if r['due']:
                    m_due = r['due']


                things = r['things']
                if things:
                    f.write('<tr>\n')
                    f.write('<td class="col-md-3"><b>%s</b></td>\n' % (repo))
                    f.write('<td>')
                    f.write('<ul class="list-unstyled">\n')
                    things = sorted(things, key=lambda k: k['title'], reverse=True)
                    for t in things:
                        if not (milestone == 'Unassigned' and t['state'] != 'open'):
                            t['icon'] = 'issue-opened'

                            if t['type'] == 'issue' and t['state'] == 'closed':
                                t['icon'] = 'issue-closed'
                            elif t['type'] == 'pull-request' and t['state'] == 'open':
                                t['icon'] = 'git-pull-request'
                            elif t['type'] == 'pull-request' and t['state'] == 'closed':
                                t['icon'] = 'git-merge'

                            f.write('<li class="thing-%(state)s">' % t)
                            f.write('<span class="text-github-%(state)s octicon octicon-%(icon)s" title="State: %(state)s"></span> ' % t)
                            f.write('<a href="%(url)s"><strong>%(title)s</strong></a> ' % t)
                            if t['comment_count']:
                                f.write('<span class="text-muted"><span class="octicon octicon-comment-discussion"></span> %(comment_count)s</span> ' % t)

                            f.write('<div style="margin-left: 16px;">')
                            f.write('<span class="text-muted">Created by</span> <a href="http://www.github.com/%(user)s">%(user)s</a> <span class="text-muted"><span class="reldate">%(created)s</span></span>' % t)
                            if t['assignee']:
                                f.write('<span class="text-muted">, Assigned to</span> <a href="http://www.github.com/%(assignee)s">%(assignee)s</a>' % t)
                            f.write('<span class="text-muted">, Updated <span class="reldate">%(updated)s</span></span> ' % t)
                            f.write('</div>')

                            f.write('</li>\n' % t)
                    f.write('</ul>\n')
                    f.write('</td>')
                    f.write('</tr>\n')
            f.write('</table>\n')

            if milestone != 'Unassigned':
                if i_closed > 0:
                    i_progress = i_closed * 100 / (i_open + i_closed) # Do this as integer maths

                f.write(
                 '''<div class="panel-footer">
                        Progress: <span class="text-muted">(%(closed)d closed, %(open)d open, due <span class="reldate">%(due)s</span>)</span>
                        <div class="progress" style="background-color: #ccc;">
                            <div class="progress-bar" role="progressbar" aria-valuenow="%(progress)d" aria-valuemin="0" aria-valuemax="100" style="width: %(progress)d%%;">%(progress)d%%</div>
                        </div>
                    </div>''' % {'progress': i_progress, 'open': i_open, 'closed': i_closed, 'due': m_due}
                )

            f.write('</div>\n')

        f.write('</div>\n')
        f.write('<p class="text-muted">Page generated <span class="reldate">%s<span></p>\n' % datetime.utcnow().replace(microsecond=0).isoformat(' '))
        f.write('</div>\n')

        f.write(FOOTER)
