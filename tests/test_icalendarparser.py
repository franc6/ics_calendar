from custom_components.ics_calendar.icalendarparser import ICalendarParser


class TestICalendarParser:
    def test_get_class_finds_rie(self):
        assert ICalendarParser.get_class("rie") is not None

    def test_get_class_finds_ics(self):
        assert ICalendarParser.get_class("ics") is not None

    def test_get_class_finds_icalevents(self):
        assert ICalendarParser.get_class("icalevents") is not None

    def test_get_class_does_not_find_unknown(self):
        assert ICalendarParser.get_class("unknown") is None

    def test_get_instance_returns_ICalendarParser(self):
        assert isinstance(ICalendarParser.get_instance("rie"), ICalendarParser)
        assert isinstance(ICalendarParser.get_instance("ics"), ICalendarParser)
        assert isinstance(ICalendarParser.get_instance("icalevents"), ICalendarParser)
