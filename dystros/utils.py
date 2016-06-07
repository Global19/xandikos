#!/usr/bin/python
#
# Dystros
# Copyright (C) 2016 Jelmer Vernooij <jelmer@jelmer.uk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License or (at your option) any later version of
# the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

from icalendar.cal import Calendar
import optparse
import os

DEFAULT_PATH = os.path.join(os.getenv("HOME"), ".config/calypso/collections/jelmer")

class CollectionSetOptionGroup(optparse.OptionGroup):
    """Return a optparser OptionGroup.

    :param parser: An OptionParser
    :param default_kind: Default kind
    :return: An OptionGroup
    """

    def __init__(self, parser, default_kind="calendar"):
        optparse.OptionGroup.__init__(self, parser, "Path Settings")
        self.add_option('--kind', type=str, dest="kind", help="List of kinds separated by commas.",
                        default=default_kind)
        self.add_option('--inputdir', type=str, dest="inputdir", help="Input directory.",
                        default=DEFAULT_PATH)


class CollectionSet(object):
    """Set of iCalendar/vCard collections."""

    def __init__(self, inputdir, kinds):
        self._inputdir = inputdir
        self._kinds = kinds

    def iter_icalendars(self):
        return list(gather_icalendars([os.path.join(self._inputdir, kind) for kind in self._kinds]))

    def iter_vevents(self):
        return extract_vevents(self.iter_icalendars())

    def iter_vtodos(self):
        return extract_vtodos(self.iter_icalendars())

    @classmethod
    def from_options(cls, opts):
        return cls(opts.inputdir, opts.kind.split(','))


def extract_vevents(calendars):
    """Extract vevents from an iterator over calendars.

    :param calendars: Iterator over Calendar objects
    :return: Iterator over Calendar subcomponents
    """
    for calendar in calendars:
        for component in calendar.subcomponents:
            if component.name == 'VEVENT':
                yield component


def extract_vtodos(calendars):
    """Extract vtodos from an iterator over calendars.

    :param calendars: Iterator over Calendar objects
    :return: Iterator over Calendar subcomponents
    """
    for calendar in calendars:
        for component in calendar.subcomponents:
            if component.name == 'VTODO':
                yield component



def statuschar(evstatus):
    """Convert an event status to a single status character.

    :param evstatus: Event status description
    :return: A single character, empty string if the status is unknown
    """
    return {'TENTATIVE': '?',
            'CONFIRMED': '.',
            'CANCELLED': '-'}.get(evstatus, '')


def format_month(dt):
    return dt.strftime("%b")


def format_daterange(start, end):
    if end is None:
        return "%d %s-?" % (start.day, format_month(start))
    if start.month == end.month:
        if start.day == end.day:
            return "%d %s" % (start.day, format_month(start))
        return "%d-%d %s" % (start.day, end.day, format_month(start))
    return "%d %s-%d %s" % (start.day, format_month(start), end.day, format_month(end))


def gather_icalendars(dirs):
    """Find all the ics files in a directory, yield components.

    :param dirs: List of directories to browse
    :return: Iterator over components found
    """
    for bp in dirs:
        for n in os.listdir(bp):
            p = os.path.join(bp, n)
            if not p.endswith(".ics"):
                continue

            yield Calendar.from_ical(open(p, 'r').read())


def asdate(dt):
    if getattr(dt, "date", None):
        a_date = dt.date()
    else:
        a_date = dt
    return dt


def cmpEvent(a, b):
    """Compare two events by date.

    :param a: First event
    :param b: Second event
    :return: -1, 0, or 1 depending on whether a < b, a == b or a > b
    """
    a = a['DTSTART'].dt
    b = b['DTSTART'].dt
    if getattr(a, "date", None):
        a_date = a.date()
        a = (a.hour, a.minute)
    else:
        a_date = a
        a = (0, 0)
    if getattr(b, "date", None):
        b_date = b.date()
        b = (b.hour, b.minute)
    else:
        b_date = b
        b = (0, 0)
    c = cmp(a_date, b_date)
    if c != 0:
        return c
    return cmp(a, b)
