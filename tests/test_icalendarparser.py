"""Test the icalendarparser class."""

from custom_components.ics_calendar.getparser import GetParser
from custom_components.ics_calendar.icalendarparser import ICalendarParser


class TestICalendarParser:
    """Test GetParser class."""

    async def test_get_parser_returns_ICalendarParser(self, hass):
        """Test that get_parser_async returns parsers of ICalendarParser."""
        assert isinstance(
            await GetParser.get_parser_async(hass, "rie"), ICalendarParser
        )
        assert isinstance(
            await GetParser.get_parser_async(hass, "ics"), ICalendarParser
        )

    async def test_get_parser_returns_None(self, hass):
        """Test that get_parser_async returns None for non-existing parser."""
        assert await GetParser.get_parser_async(hass, "unknown") is None
