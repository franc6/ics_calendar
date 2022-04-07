"""Support for recurring_ical_events parser."""
from datetime import date, datetime, timedelta

import recurring_ical_events as rie
from icalendar import Calendar

from ..icalendarparser import ICalendarParser


class ParserRIE(ICalendarParser):
    """Provide parser using recurring_ical_events."""

    oneday = timedelta(days=1)
    oneday2 = timedelta(hours=23, minutes=59, seconds=59)

    @staticmethod
    def get_event_list(
        content: str, start: datetime, end: datetime, include_all_day: bool
    ) -> str:
        """Get a list of events.

        Gets the events from start to end, including or excluding all day events.
        :param content is the calendar data
        :type str
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

        calendar = Calendar.from_ical(content)

        if calendar is not None:
            for event in rie.of(calendar).between(start, end):
                start, end, all_day = ParserRIE.is_all_day(event)

                if all_day and not include_all_day:
                    continue

                uid = None
                if event.get("UID"):
                    uid = event.get("UID")

                data = {
                    "uid": uid,
                    "summary": event.get("SUMMARY"),
                    "start": start,
                    "end": end,
                    "location": event.get("LOCATION"),
                    "description": event.get("DESCRIPTION"),
                    "all_day": all_day,
                }
                # Note that we return a formatted date for start and end here,
                # but a different format for get_current_event!
                event_list.append(data)

        return event_list

    @staticmethod
    def get_current_event(
        content: str, include_all_day: bool, now: datetime, days: int
    ):
        """Get the current or next event.

        Gets the current event, or the next upcoming event with in the
        specified number of days, if there is no current event.
        :param content is the calendar data
        :type str
        :param include_all_day if true, all day events will be included.
        :type boolean
        :param now the current date and time
        :type datetime
        :param days the number of days to check for an upcoming event
        :type int
        :returns an event or None
        """
        calendar = Calendar.from_ical(content)

        if calendar is None:
            return None

        temp_event = None
        end = now + timedelta(days=days)
        for event in rie.of(calendar).between(now, end):
            start, end, all_day = ParserRIE.is_all_day(event)

            if all_day and not include_all_day:
                continue

            if temp_event is None:
                temp_event = event
                temp_start = start
                temp_end = end
                temp_all_day = all_day
            elif temp_end > end and start <= temp_start:
                temp_event = event
                temp_start = start
                temp_end = end
                temp_all_day = all_day

        if temp_event is None:
            return None

        return {
            "summary": temp_event.get("SUMMARY"),
            "start": temp_start,
            "end": temp_end,
            "location": temp_event.get("LOCATION"),
            "description": temp_event.get("DESCRIPTION"),
            "all_day": temp_all_day,
        }

    @staticmethod
    def get_date(date_time) -> datetime:
        """Get datetime with timezone information.

        If a date object is passed, it will first have a time component added,
        set to 0.
        :param date_time The date or datetime object
        :type date_time datetime or date
        :type: bool
        :returns The datetime.
        :rtype datetime
        """
        # Must use type here, since a datetime is also a date!
        if type(date_time) == date:  # pylint: disable=C0123
            date_time = datetime.combine(date_time, datetime.min.time())
        return date_time.astimezone()

    @staticmethod
    def is_all_day(event):
        """Determine if the event is an all day event.

        Return all day status and start and end times for the event.
        :param event The event to examine
        """
        start = ParserRIE.get_date(event.get("DTSTART").dt)
        end = ParserRIE.get_date(event.get("DTEND").dt)
        all_day = False
        diff = event.get("DURATION")
        if diff is not None:
            diff = diff.dt
        else:
            diff = end - start
        if diff in {ParserRIE.oneday, ParserRIE.oneday2} and all(
            x == 0 for x in [start.hour, start.minute, start.second]
        ):
            all_day = True

        return start, end, all_day
