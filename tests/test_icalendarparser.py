"""Test the icalendarparser class."""

from custom_components.ics_calendar.icalendarparser import ICalendarParser


class TestICalendarParser:
    """Test ICalendarParser class."""

    def test_get_class_finds_rie(self):
        """Test get_class returns the rie parser."""
        assert ICalendarParser.get_class("rie") is not None

    def test_get_class_finds_ics(self):
        """Test get_class returns the ics parser."""
        assert ICalendarParser.get_class("ics") is not None

    def test_get_class_does_not_find_unknown(self):
        """Test get_class does not find non-existing parser."""
        assert ICalendarParser.get_class("unknown") is None

    def test_get_instance_returns_ICalendarParser(self):
        """Test that get_instance returns instances of ICalendarParser."""
        assert isinstance(ICalendarParser.get_instance("rie"), ICalendarParser)
        assert isinstance(ICalendarParser.get_instance("ics"), ICalendarParser)

    def test_get_instance_returns_None(self):
        """Test that get_instance returns None for non-existing parser."""
        assert ICalendarParser.get_instance("unknown") is None
