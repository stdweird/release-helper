"""
Configure milestones
"""
import logging
from datetime import date, datetime, timedelta
from calendar import monthrange


MST_BACKLOG = 'Backlog'
MST_LEGACY = 'Legacy'


class MileStone(object):
    def __init__(self, milestone=None, year_month=None, title=None, release=None):
        """
        Create a milestone instance from one-of
            milestone: another milestone instance
            year_month: a tuple (year, month)
            title: a title (i.e. a string with title format)

        release is a dictionary with release dates (from CONFIG[RELEASES])
        """
        self.year = None
        self.month = None
        self.point = None

        self.milestone = None

        self.release = release

        if milestone:
            self.milestone = milestone
            self.from_title(milestone.title)
        elif year_month:
            self.from_year_month(year_month)
        elif title:
            self.from_title(title)

    def from_year_month(self, year_month):
        self.year = year_month[0]
        self.month = year_month[1]

    def from_title(self, title):
        try:
            parts = map(int, title.split('.'))
        except ValueError as e:
            raise("Failed to convert title %s to milestone: %s" % (title, e))

        self.year = 2000 + parts[0]
        self.month = parts[1]
        if len(parts) >= 3:
            self.point = parts[2]

    def edit(self, *args, **kwargs):
        """Edit this milestone"""
        if self.milestone is None:
            raise('MileStone: cannot edit without milstone attribute')

        # Insert title
        args = [self.title()] + list(args)

        self.milestone.edit(*args, **kwargs)

    def set_state(self):
        """Open / close milestone"""
        now = datetime.now() - timedelta(1)
        due_on = self.milestone.due_on

        if due_on >= now:
            state = 'open'
            msg = 'opening'
        else:
            state = 'closed'
            msg = 'closing'

        self.edit(state=state)
        logging.info("  %s milestone %s", msg, self)

    def title(self):
        """Make the title"""
        if self.year is None:
            raise('MileStone: no year set')
        if self.month is None:
            raise('MileStone: no month set')
        txt = '%02d.%02d' % (self.year - 2000, self.month)
        if self.point is not None:
            txt += ".%d" % self.point
        return txt

    def create(self, repo):
        """
        Add new milestone to repo and set new instance as milestone attribute
        """

        logging.info('Creating milestone %s in repo %s', self, repo.name)
        # Do not pass due_on here, see https://github.com/PyGithub/PyGithub/issues/396
        milestone = repo.create_milestone(title=self.title())
        if self.milestone:
            logging.debug("Replacing current milestone %s with newly created one %s", self.milestone, milestone)
        self.milestone = milestone
        self.set_due_date()

    def get_due(self, from_title=None):
        """
        Return the due_on date

        If release is set, use the target date.
        If not (or from_title is true), use the year/month (i.e. from the title)
        """

        if self.release and not from_title:
            due_on = self.release['target']
            logging.debug('Due date %s from release target for %s', due_on, self)
        else:
            day = monthrange(self.year, self.month)[-1]
            due_on = date(self.year, self.month, day)

            logging.debug("Generated due date %s for %s", due_on, self)

        return due_on

    def set_due_date(self):
        """Set the due date"""
        if self.milestone:
            due = self.get_due()
            if self.milestone.due_on != due:
                logging.info("Set due date from %s to %s", self.milestone.due_on, due)
                self.edit(due_on=due)
            else:
                logging.debug("No resetting milestone due date to same due %s", due)
        else:
            logging.warn("No milestone instance set for set_due_date")

    def __str__(self):
        return self.title()

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.year == other.year
                and self.month == other.month
                and self.point == other.point) # TODO: issue with None == integer?

    def __ne__(self, other):
        return not self.__eq__(other)


def add_months(sourcedate, months):
    """
    Add months to sourcedate, return new date
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day, monthrange(year, month)[1])
    return date(year, month, day)


def milestones_from_releases(releases):
    """
    Generate a list of  milestones based on releases
    """
    milestones = [MileStone(title=title, release=release) for title, release in releases.items()]
    milestones.sort(key=lambda s: s.release['target'])

    logging.debug("Milestones from releases: %s", ", ".join(map(str, milestones)))

    return milestones


def generate_milestones(milestones=4, months=2, today=None):
    """
    Generate the next milestones (each spanning months)
    """
    if today is None:
        today = date.today()
    month = today.month

    # Seek till multiple of months
    while month % months > 0:
        month += 1

    start = date(today.year, month, 1)

    m_future = []
    for m in range(1, milestones):
        n = add_months(start, m*months)
        m_future.append(MileStone(year_month=(n.year, n.month)))

    logging.debug("Generated %d milestones (duration %d months) from today %s (start %s): %s",
                  milestones, months, today, start, m_future)

    return m_future


def mkms(repo, state, **kwargs):
    """
    Return the milestones in state state (any named args are passed to the get_milestones API method)
    """
    kwargs['state'] = state
    return [MileStone(milestone=m) for m in repo.get_milestones(**kwargs)]


def configure_milestones(repo, milestones):
    """
    Open / reopen milestones for repo
    Set correct due date from release info from milestones list
    """

    # TODO: change state somehow

    logging.debug("configure milestones for repo %s", repo.name)

    # These MileStone instances have no release data
    m_open = mkms(repo, 'open')
    m_closed = mkms(repo, 'closed')
    m_all = m_open + m_closed

    for m in m_closed:
        logging.debug("  Found closed milestone %s", m)
        m.set_state()

    for m in m_open:
        logging.debug("  Found open milestone %s", m)

        if m.point is None:
            if m in milestones:
                m.release = milestones[milestones.index(m)].release
                logging.debug("Adding release data %s to open milestone %s", m.release, m)
            else:
                logging.warn("Configuring open milestone %s in repo but not found in releases. Date will be generated", m, repo.name)
            m.set_due_date()
            m.set_state()
        else:
            logging.info('   Not modifying open point release %s in repo %s', m, repo.name)

    for m in milestones:
        if m in m_all:
            logging.debug('Future milestone %s already in open/closed in repo %s', m, repo.name)
        else:
            m.create(repo)


def bump(repo, months=2, releases=None):
    """
    Bump the open milestones for the repository.

    This shifts the due date by months and changes the title accordingly (preserves issues/prs).

    If a release is present, it assumes it is the old release data (so do not change it before bump)
    and than it also bumps the release start, rcs and target dates.

    The release data is only used for generating new/bumped release config data.

    Return the new releases config text (if any)
    """

    # These have to be ordered, such that bumping the milestone
    # Does not generate an already existing one
    # Sort most future one first
    m_open = mkms(repo, 'open', sort='due_date', direction='desc')

    u_release_txt = []
    for m in m_open:
        logging.debug("Found open milestone %s", m)

        if m.point is None:
            # get_due from title only
            due_from_title = m.get_due(from_title=True)
            due_updated = add_months(due_from_title, months)

            # Make a new MileStone
            m_u = MileStone(year_month=(due_updated.year, due_updated.month))

            # Reuse the original milestone instance
            m_u.milestone = m.milestone

            # set_due_date will now use the original milestone instance
            # to modify the due date and the title
            logging.info("Bump milestone %s (due %s) to new %s (due %s) for repo %s",
                         m, due_from_title, m_u, m_u.get_due(), repo.name)
            m_u.set_due_date()

            # Generate bumped release config data
            release_u = None
            release = releases.get(m.title(), None)
            if release:
                release_u = [add_months(release[k], months).strftime('%Y-m-%d') for k in ['start', 'rcs', 'target']]
                u_release_txt.append(','.join(release_u))
        else:
            logging.info('Not modifying open point release %s', m)

    return "\n".join(u_release_txt)

def sort_milestones(msts, add_special=True):
    """
    Return sorted milestones
    """
    # TODO: replace by MileStone instances with ordering support
    # special is ordered
    special = (MST_BACKLOG, MST_LEGACY,)

    # milestones are sorted keys on date, with Backlog and Legacy last
    milestones = [x for x in msts if x not in special]
    milestones.sort(key=lambda s: [int(u) for u in s.split('.')])

    if add_special:
        for mst in special:
            if mst in msts:
                milestones.append(mst)

    return milestones
