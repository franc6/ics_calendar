"""Support for ics parser."""
import re
from datetime import datetime, timedelta

from arrow import Arrow, get as arrowget
from ics import Calendar

from ..icalendarparser import ICalendarParser


class ParserICS(ICalendarParser):
    """Class to provide parser using ics module."""

    def __init__(self):
        """Construct ParserICS."""
        self._re_method = re.compile("^METHOD:.*$", flags=re.MULTILINE)
        self._calendar = None

    def set_content(self, content: str):
        """Parse content into a calendar object.

        This must be called at least once before get_event_list or
        get_current_event.
        :param content is the calendar data
        :type content str
        """
        self._calendar = Calendar(re.sub(self._re_method, "", content))

    def get_event_list(self, start, end, include_all_day: bool) -> list:
        """Get a list of events.

        Gets the events from start to end, including or excluding all day
        events.
        :param start the earliest start time of events to return
        :type datetime
        :param end the latest start time of events to return
        :type datetime
        :param include_all_day if true, all day events will be included.
        :type boolean
        :returns a list of events, or an empty list
        :rtype list
        """
        event_list = []

        if self._calendar is not None:
            # ics 0.8 takes datetime not Arrow objects
            # ar_start = start
            # ar_end = end
            ar_start = arrowget(start)
            ar_end = arrowget(end)

            for event in self._calendar.timeline.included(ar_start, ar_end):
                if event.all_day and not include_all_day:
                    continue
                uid = None
                summary = ""
                if hasattr(event, "uid"):
                    uid = event.uid
                # ics 0.8 uses 'summary' reliably, older versions use 'name'
                # if hasattr(event, "summary"):
                #    summary = event.summary
                # elif hasattr(event, "name"):
                summary = event.name
                data = {
                    "uid": uid,
                    "summary": summary,
                    "start": ParserICS.get_date(event.begin, event.all_day),
                    "end": ParserICS.get_date(event.end, event.all_day),
                    "location": event.location,
                    "description": event.description,
                    "all_day": event.all_day,
                }
                # Note that we return a formatted date for start and end here,
                # but a different format for get_current_event!
                event_list.append(data)

        return event_list

    def get_current_event(
        self, include_all_day: bool, now: datetime, days: int
    ):
        """Get the current or next event.

        Gets the current event, or the next upcoming event with in the
        specified number of days, if there is no current event.
        :param include_all_day if true, all day events will be included.
        :type boolean
        :param now the current date and time
        :type datetime
        :param days the number of days to check for an upcoming event
        :type int
        :returns an event or None
        """
        if self._calendar is None:
            return None

        temp_event = None
        end = now + timedelta(days=days)
        for event in self._calendar.timeline.included(
            arrowget(now), arrowget(end)
        ):
            if event.all_day and not include_all_day:
                continue
            if ParserICS.is_event_newer(temp_event, event):
                temp_event = event

        if temp_event is None:
            return None
        # if hasattr(event, "summary"):
        # summary = temp_event.summary
        # elif hasattr(event, "name"):
        summary = temp_event.name
        return {
            "summary": summary,
            "start": ParserICS.get_date(temp_event.begin, temp_event.all_day),
            "end": ParserICS.get_date(temp_event.end, temp_event.all_day),
            "location": temp_event.location,
            "description": temp_event.description,
            "all_day": temp_event.all_day,
        }

    @staticmethod
    def is_event_newer(check_event, event):
        """Determine if check_event is newer than event."""
        return check_event is None or (
            check_event.end > event.end and check_event.begin <= event.begin
        )

    @staticmethod
    def get_date(arw: Arrow, is_all_day: bool) -> datetime:
        """Get datetime.

        :param arw The arrow object representing the date.
        :type Arrow
        :param is_all_day If true, the returned datetime will have the time
        component set to 0.
        :type: bool
        :returns The datetime.
        :rtype datetime
        """
        if isinstance(arw, Arrow):
            if is_all_day:
                arw = arw.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo="local"
                )
            return arw.datetime
        # else:
        # if arw.tzinfo is None or arw.tzinfo.utcoffset(arw) is None
        #     or is_all_day:
        #        arw = arw.astimezone()
        #
        return arw
