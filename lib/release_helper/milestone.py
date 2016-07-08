"""
Configure milestones
"""
import logging
from datetime import date, datetime, timedelta
from calendar import monthrange


class MileStone(object):
    def __init__(self, milestone=None, year_month=None, title=None):
        self.year = None
        self.month = None
        self.point = None

        self.milestone = None

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
        args = [self.title()] + args

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
        """Add new milestone to repo"""

        due = self.get_due()
        logging.info('Creating milestone %s in repo %s (due %s)', self, repo.nam, due)
        repo.create_milestone(title=self.title(), due_on=due)

    def get_due(self):
        """Create the due_on date"""

        day = monthrange(self.year, self.month)[-1]
        due_on = date(self.year, self.month, day)

        # TODO: from config file
        if self.title() == '16.4':
            due_on = date(2016, 5, 20)
            logging.info('Pushed back due date for 16.4 to %s', due_on)

        logging.debug("Generated due_on date %s for %s", due_on, self)

        return due_on

    def set_due_date(self):
        """Set the due date"""
        due = self.get_due()
        if self.milestone.due_on != due:
            self.edit(due_on=due)

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


def generate_milestones(milestones=4, months=2, today=None):
    """
    Generate the next year/month tuples for the next milestones (each spanning months)
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


def configure(repo, milestones=None):
    """
    Open / reopen milestones for repo
    milestones is a year/month tuple
    """

    if milestones is None:
        milestones = generate_milestones()

    logging.debug("configure milestones for repo %s", repo.name)

    m_open = mkms(repo, 'open')
    m_closed = mkms(repo, 'closed')
    m_all = m_open + m_closed

    for m in m_closed:
        logging.debug("  Found closed milestone %s", m)
        m.set_state()

    for m in m_open:
        logging.debug("  Found open milestone %s", m)

        if m.point is None:
            m.set_due_date()
            m.set_state()
        else:
            logging.info('   Not modifying open point release %s', m)

    for m in milestones:
        if m in m_all:
            logging.debug('Future milestone %s already in open/closed', m)
        else:
            m.create(repo)


def bump(repo, months=2):
    """
    Bump the open milestones for the repository.
    This shifts the due date by months and changes the title accordingly.
    """

    # These have to be ordered, such that bumping the milestone
    # Does not generate an already existing one
    # Sort most future one first
    m_open = mkms(repo, 'open', sort='due_date', direction='desc')

    for m in m_open:
        logging.debug("Found open milestone %s", m)

        if m.point is None:
            due = m.get_due()
            due_updated = add_months(due, months)

            # Make a new MileStone
            m_u = MileStone(year_month=(due_updated.year, due_updated.month))

            # Reuse the original milestone instance
            m_u.milestone = m.milestone
            # set_due_date with the original milestone instance will modify the due date and the title
            logging.info("Bump milestone %s (due %s) to new %s (due %s) for repo %s",
                         m, due, m_u, m_u.get_due(), repo.name)
            m_u.set_due_date()
        else:
            logging.info('Not modifying open point release %s', m)
