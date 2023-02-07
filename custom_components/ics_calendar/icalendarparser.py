"""Provide ICalendarParser class."""
import importlib
from datetime import datetime
from typing import Optional

from homeassistant.components.calendar import CalendarEvent

from .filter import Filter


class ICalendarParser:
    """Provide interface for various parser classes.

    The class provides a static method , get_instace, to get a parser instance.
    The non static methods allow this class to act as an "interface" for the
    parser classes.
    """

    @staticmethod
    def get_class(parser: str):
        """Get the class of the requested parser."""
        parser_module_name = ".parsers.parser_" + parser
        parser = "Parser" + parser.upper()
        try:
            module = importlib.import_module(parser_module_name, __package__)
            return getattr(module, parser)
        except ImportError:
            return None

    @staticmethod
    def get_instance(parser: str, *args):
        """Get an instance of the requested parser."""
        parser_cls = ICalendarParser.get_class(parser)
        if parser_cls is not None:
            return parser_cls(*args)
        return None

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
