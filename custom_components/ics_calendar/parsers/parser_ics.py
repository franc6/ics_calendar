"""Support for ics parser."""
import re
from datetime import date, datetime, timedelta
from typing import Optional, Union

from arrow import Arrow, get as arrowget
from homeassistant.components.calendar import CalendarEvent
from ics import Calendar

from ..filter import Filter
from ..icalendarparser import ICalendarParser
from ..utility import compare_event_dates


class ParserICS(ICalendarParser):
    """Class to provide parser using ics module."""

    def __init__(self):
        """Construct ParserICS."""
        self._re_method = re.compile("^METHOD:.*$", flags=re.MULTILINE)
        self._calendar = None
        self._filter = Filter("", "")

    def set_content(self, content: str):
        """Parse content into a calendar object.

        This must be called at least once before get_event_list or
        get_current_event.
        :param content is the calendar data
        :type content str
        """
        self._calendar = Calendar(re.sub(self._re_method, "", content))

    def set_filter(self, filt: Filter):
        """Set a Filter object to filter events.

        :param filt: The Filter object
        :type exclude: Filter
        """
        self._filter = filt

    def get_event_list(
        self, start, end, include_all_day: bool, offset_hours: int = 0
    ) -> list[CalendarEvent]:
        """Get a list of events.

        Gets the events from start to end, including or excluding all day
        events.
        :param start the earliest start time of events to return
        :type datetime
        :param end the latest start time of events to return
        :type datetime
        :param include_all_day if true, all day events will be included.
        :type boolean
        :param offset_hours the number of hours to offset the event
        :type offset_hours int
        :returns a list of events, or an empty list
        :rtype list[CalendarEvent]
        """
        event_list: list[CalendarEvent] = []

        if self._calendar is not None:
            # ics 0.8 takes datetime not Arrow objects
            # ar_start = start
            # ar_end = end
            ar_start = arrowget(start - timedelta(hours=offset_hours))
            ar_end = arrowget(end - timedelta(hours=offset_hours))

            for event in self._calendar.timeline.included(ar_start, ar_end):
                if event.all_day and not include_all_day:
                    continue
                summary: str = ""
                # ics 0.8 uses 'summary' reliably, older versions use 'name'
                # if hasattr(event, "summary"):
                #    summary = event.summary
                # elif hasattr(event, "name"):
                summary = event.name
                calendar_event: CalendarEvent = CalendarEvent(
                    summary=summary,
                    start=ParserICS.get_date(
                        event.begin, event.all_day, offset_hours
                    ),
                    end=ParserICS.get_date(
                        event.end, event.all_day, offset_hours
                    ),
                    location=event.location,
                    description=event.description,
                )
                if self._filter.filter_event(calendar_event):
                    event_list.append(calendar_event)

        return event_list

    def get_current_event(  # noqa: $701
        self,
        include_all_day: bool,
        now: datetime,
        days: int,
        offset_hours: int = 0,
    ) -> Optional[CalendarEvent]:
        """Get the current or next event.

        Gets the current event, or the next upcoming event with in the
        specified number of days, if there is no current event.
        :param include_all_day if true, all day events will be included.
        :type boolean
        :param now the current date and time
        :type datetime
        :param days the number of days to check for an upcoming event
        :type int
        :param offset_hours the number of hours to offset the event
        :type int
        :returns a CalendarEvent or None
        """
        if self._calendar is None:
            return None

        temp_event = None
        now = now - timedelta(offset_hours)
        end = now + timedelta(days=days)
        for event in self._calendar.timeline.included(
            arrowget(now), arrowget(end)
        ):
            if event.all_day and not include_all_day:
                continue

            if not self._filter.filter(event.name, event.description):
                continue

            if temp_event is None or compare_event_dates(
                now,
                temp_event.end,
                temp_event.begin,
                temp_event.all_day,
                event.end,
                event.begin,
                event.all_day,
            ):
                temp_event = event

        if temp_event is None:
            return None
        # if hasattr(event, "summary"):
        # summary = temp_event.summary
        # elif hasattr(event, "name"):
        summary = temp_event.name
        return CalendarEvent(
            summary=summary,
            start=ParserICS.get_date(
                temp_event.begin, temp_event.all_day, offset_hours
            ),
            end=ParserICS.get_date(
                temp_event.end, temp_event.all_day, offset_hours
            ),
            location=temp_event.location,
            description=temp_event.description,
        )

    @staticmethod
    def get_date(
        arw: Arrow, is_all_day: bool, offset_hours: int
    ) -> Union[datetime, date]:
        """Get datetime.

        :param arw The arrow object representing the date.
        :type Arrow
        :param is_all_day If true, the returned datetime will have the time
        component set to 0.
        :type: bool
        :param offset_hours the number of hours to offset the event
        :type int
        :returns The datetime.
        :rtype datetime
        """
        # if isinstance(arw, Arrow):
        if is_all_day:
            return arw.date()
        # else:
        # if arw.tzinfo is None or arw.tzinfo.utcoffset(arw) is None
        #     or is_all_day:
        #        arw = arw.astimezone()
        # if is_all_day:
        #    return arw.date()
        #
        arw = arw.shift(hours=offset_hours)

        return_value = arw.datetime
        if return_value.tzinfo is None:
            return_value = return_value.astimezone()
        return return_value
