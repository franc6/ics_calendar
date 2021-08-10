import pytest
from dateutil import parser as dtparser
from custom_components.ics_calendar.icalendarparser import ICalendarParser
import ics
import icalevents

class TestParsers:

    # Issue 6 is a problem for ics still!
    @pytest.mark.xfail(raises=ics.grammar.parse.ParseError)
    @pytest.mark.parametrize('fileName', ['issue6.ics'])
    def test_issue_six_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-01-31T23:59:59"), False)
        assert event_list is not None
        assert 1 == len(event_list)
        
    @pytest.mark.parametrize('fileName', ['issue6.ics'])
    def test_issue_six_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-01-31T23:59:59"), False)
        assert event_list is not None
        assert 1 == len(event_list)

    # ics isn't showing the recurring events!
    @pytest.mark.xfail()   
    @pytest.mark.parametrize('fileName', ['issue8.ics'])
    def test_issue_eight_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-06-15T23:59:59"), True)
        assert event_list is not None
        assert 3 == len(event_list)

    # Bug in RRULE
    @pytest.mark.xfail(raises=ValueError)
    @pytest.mark.parametrize('fileName', ['issue8.ics'])
    def test_issue_eight_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-06-15T23:59:59"), True)
        assert event_list is not None
        assert 3 == len(event_list)
        
    # ics isn't showing the recurring events!
    @pytest.mark.xfail()
    @pytest.mark.parametrize('fileName', ['issue17.ics'])
    def test_issue_seventeen_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2020-09-14T00:00:00"), dtparser.parse("2020-09-29T23:59:59"), True)
        assert event_list is not None
        assert 25 == len(event_list)
        
    @pytest.mark.parametrize('fileName', ['issue17.ics'])
    def test_issue_seventeen_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2020-09-14T00:00:00"), dtparser.parse("2020-09-29T23:59:59"), True)
        assert event_list is not None
        assert 25 == len(event_list)

    @pytest.mark.parametrize('fileName', ['issue34.ics'])
    def test_issue_thirty_four_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2021-01-01T00:00:00"), dtparser.parse("2021-12-31T23:59:59"), True)
        assert event_list is not None
        assert 123 == len(event_list)
        
    @pytest.mark.parametrize('fileName', ['issue34.ics'])
    def test_issue_thirty_four_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2021-01-01T00:00:00"), dtparser.parse("2021-12-31T23:59:59"), True)
        assert event_list is not None
        assert 123 == len(event_list)
        