"""Support for recurring_ical_events parser."""
from datetime import date, datetime, timedelta
from typing import Optional, Union

import recurring_ical_events as rie
from homeassistant.components.calendar import CalendarEvent
from icalendar import Calendar

from ..filter import Filter
from ..icalendarparser import ICalendarParser
from ..utility import compare_event_dates


class ParserRIE(ICalendarParser):
    """Provide parser using recurring_ical_events."""

    def __init__(self):
        """Construct ParserRIE."""
        self._calendar = None
        self.oneday = timedelta(days=1)
        self.oneday2 = timedelta(hours=23, minutes=59, seconds=59)
        self._filter = Filter("", "")

    def set_content(self, content: str):
        """Parse content into a calendar object.

        This must be called at least once before get_event_list or
        get_current_event.
        :param content is the calendar data
        :type content str
        """
        self._calendar = Calendar.from_ical(content)

    def set_filter(self, filt: Filter):
        """Set a Filter object to filter events.

        :param filt: The Filter object
        :type exclude: Filter
        """
        self._filter = filt

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
            for event in rie.of(self._calendar).between(
                start - timedelta(hours=offset_hours),
                end - timedelta(hours=offset_hours),
            ):
                start, end, all_day = self.is_all_day(event, offset_hours)

                if all_day and not include_all_day:
                    continue

                calendar_event: CalendarEvent = CalendarEvent(
                    summary=event.get("SUMMARY"),
                    start=start,
                    end=end,
                    location=event.get("LOCATION"),
                    description=event.get("DESCRIPTION"),
                )
                if self._filter.filter_event(calendar_event):
                    event_list.append(calendar_event)

        return event_list

    def get_current_event(  # noqa: R701
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
        :type offset_hours int
        :returns a CalendarEvent or None
        """
        if self._calendar is None:
            return None

        temp_event: CalendarEvent = None
        temp_start: date | datetime = None
        temp_end: date | datetime = None
        temp_all_day: bool = None
        end: datetime = now + timedelta(days=days)
        for event in rie.of(self._calendar).between(
            now - timedelta(hours=offset_hours),
            end - timedelta(hours=offset_hours),
        ):
            start, end, all_day = self.is_all_day(event, offset_hours)

            if all_day and not include_all_day:
                continue

            if not self._filter.filter(
                event.get("SUMMARY"), event.get("DESCRIPTION")
            ):
                continue

            if temp_start is None or compare_event_dates(
                now, temp_end, temp_start, temp_all_day, end, start, all_day
            ):
                temp_event = event
                temp_start = start
                temp_end = end
                temp_all_day = all_day

        if temp_event is None:
            return None

        return CalendarEvent(
            summary=temp_event.get("SUMMARY"),
            start=temp_start,
            end=temp_end,
            location=temp_event.get("LOCATION"),
            description=temp_event.get("DESCRIPTION"),
        )

    @staticmethod
    def get_date(date_time) -> Union[datetime, date]:
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
        if isinstance(date_time, date) and not isinstance(date_time, datetime):
            date_time = datetime.combine(date_time, datetime.min.time())
        return date_time.astimezone()

    def is_all_day(self, event, offset_hours: int):
        """Determine if the event is an all day event.

        Return all day status and start and end times for the event.
        :param event The event to examine
        :param offset_hours the number of hours to offset the event
        :type offset_hours int
        """
        start: datetime | date = ParserRIE.get_date(event.get("DTSTART").dt)
        end: datetime | date = ParserRIE.get_date(event.get("DTEND").dt)
        all_day = False
        diff = event.get("DURATION")
        if diff is not None:
            diff = diff.dt
        else:
            diff = end - start
        if (start == end or diff in {self.oneday, self.oneday2}) and all(
            x == 0 for x in [start.hour, start.minute, start.second]
        ):
            # if all_day, start and end must be date, not datetime!
            start = start.date()
            end = end.date()
            all_day = True
        else:
            start = start + timedelta(hours=offset_hours)
            end = end + timedelta(hours=offset_hours)
            if start.tzinfo is None:
                start = start.astimezone()
            if end.tzinfo is None:
                end = end.astimezone()

        return start, end, all_day
