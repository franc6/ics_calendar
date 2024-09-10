"""Test the icalendarparser class."""

from custom_components.ics_calendar.getparser import GetParser
from custom_components.ics_calendar.icalendarparser import ICalendarParser


class TestICalendarParser:
    """Test GetParser class."""

    def test_get_parser_returns_ICalendarParser(self):
        """Test that get_parser returns parsers of ICalendarParser."""
        assert isinstance(GetParser.get_parser("rie"), ICalendarParser)
        assert isinstance(GetParser.get_parser("ics"), ICalendarParser)

    def test_get_parser_returns_None(self):
        """Test that get_parser returns None for non-existing parser."""
        assert GetParser.get_parser("unknown") is None
