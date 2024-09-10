"""Provide ICalendarParser class."""

from datetime import datetime
from typing import Optional

from homeassistant.components.calendar import CalendarEvent

from .filter import Filter


class ICalendarParser:
    """Provide interface for various parser classes."""

    def set_content(self, content: str):
        """Parse content into a calendar object.

        This must be called at least once before get_event_list or
        get_current_event.
        :param content is the calendar data
        :type content str
        """

    def set_filter(self, filt: Filter):
        """Set a Filter object to filter events.

        :param filt: The Filter object
        :type exclude: Filter
        """

    def get_event_list(
        self,
        start: datetime,
        end: datetime,
        include_all_day: bool,
        offset_hours: int = 0,
    ) -> list[CalendarEvent]:
        """Get a list of events.

        Gets the events from start to end, including or excluding all day
        events.
        :param start the earliest start time of events to return
        :type start datetime
        :param end the latest start time of events to return
        :type end datetime
        :param include_all_day if true, all day events will be included.
        :type include_all_day boolean
        :param offset_hours the number of hours to offset the event
        :type offset_hours int
        :returns a list of events, or an empty list
        :rtype list[CalendarEvent]
        """

    def get_current_event(
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
        :type include_all_day boolean
        :param now the current date and time
        :type now datetime
        :param days the number of days to check for an upcoming event
        :type days int
        :param offset_hours the number of hours to offset the event
        :type offset_hours int
        :returns a CalendarEvent or None
        """
