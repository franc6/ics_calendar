import pytest
from dateutil import parser as dtparser
from custom_components.ics_calendar.icalendarparser import ICalendarParser
import ics
import icalevents

class TestParsers:

    # Issue 6 is a problem for ics still!
    @pytest.mark.xfail(raises=ics.grammar.parse.ParseError)
    # ICS 0.8 uses a different class hierarchy for ParseError
    #@pytest.mark.xfail(raises=ics.contentline.container.ParseError)
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

    @pytest.mark.parametrize('fileName', ['issue8.ics'])
    def test_issue_eight_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-06-15T23:59:59"), True)
        assert event_list is not None
        # ics isn't showing the recurring events!
        #assert 2 == len(event_list)
        assert 1 == len(event_list)

    # Bug in RRULE
    @pytest.mark.parametrize('fileName', ['issue8.ics'])
    def test_issue_eight_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-06-15T23:59:59"), True)
        assert event_list is not None
        assert 2 == len(event_list)

    @pytest.mark.parametrize('fileName', ['issue17.ics'])
    def test_issue_seventeen_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2020-09-14T00:00:00-0400"), dtparser.parse("2020-09-29T23:59:59-0400"), True)
        assert event_list is not None
        # ics isn't showing the recurring events!
        #assert 25 == len(event_list)
        assert 3 == len(event_list)
        # TODO Make these checks generic, and ensure the time comparison isn't a string!
        assert "2020-09-14T14:00:00+08:00" == event_list[0]['start']
        assert "summary1" == event_list[0]['summary']
        assert "2020-09-15T09:55:00+08:00" == event_list[1]['start']
        assert "summary2" == event_list[1]['summary']
        # ics gets the wrong event here...
        #assert "2020-09-14T08:00:00+08:00" == event_list[2]['start']
        assert "2020-09-17T09:55:00+08:00" == event_list[2]['start']
        assert "summary12" == event_list[2]['summary']

    @pytest.mark.parametrize('fileName', ['issue17.ics'])
    def test_issue_seventeen_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2020-09-14T00:00:00-0400"), dtparser.parse("2020-09-29T23:59:59-0400"), True)
        assert event_list is not None
        assert 25 == len(event_list)
        # TODO Make these checks generic, and ensure the time comparison isn't a string!
        assert "2020-09-14T02:00:00.000000-0400" == event_list[0]['start']
        assert "summary1" == event_list[0]['summary']
        assert "2020-09-21T02:00:00.000000-0400" == event_list[1]['start']
        assert "summary1" == event_list[1]['summary']
        assert "2020-09-28T02:00:00.000000-0400" == event_list[2]['start']
        assert "summary1" == event_list[2]['summary']

        assert "2020-09-14T21:55:00.000000-0400" == event_list[3]['start']
        assert "summary2" == event_list[3]['summary']
        assert "2020-09-21T21:55:00.000000-0400" == event_list[4]['start']
        assert "summary2" == event_list[4]['summary']
        assert "2020-09-28T21:55:00.000000-0400" == event_list[5]['start']
        assert "summary2" == event_list[5]['summary']

        assert "2020-09-20T20:00:00.000000-0400" == event_list[6]['start']
        assert "summary3" == event_list[6]['summary']
        assert "2020-09-27T20:00:00.000000-0400" == event_list[7]['start']
        assert "summary3" == event_list[7]['summary']

        assert "2020-09-14T20:00:00.000000-0400" == event_list[8]['start']
        assert "summary4" == event_list[8]['summary']
        assert "2020-09-21T20:00:00.000000-0400" == event_list[9]['start']
        assert "summary4" == event_list[9]['summary']
        assert "2020-09-28T20:00:00.000000-0400" == event_list[10]['start']
        assert "summary4" == event_list[10]['summary']

        assert "2020-09-15T20:00:00.000000-0400" == event_list[11]['start']
        assert "summary6" == event_list[11]['summary']
        assert "2020-09-22T20:00:00.000000-0400" == event_list[12]['start']
        assert "summary6" == event_list[12]['summary']
        assert "2020-09-29T20:00:00.000000-0400" == event_list[13]['start']
        assert "summary6" == event_list[13]['summary']

        assert "2020-09-20T21:55:00.000000-0400" == event_list[14]['start']
        assert "summary8" == event_list[14]['summary']
        assert "2020-09-27T21:55:00.000000-0400" == event_list[15]['start']
        assert "summary8" == event_list[15]['summary']

        assert "2020-09-15T21:55:00.000000-0400" == event_list[16]['start']
        assert "summary9" == event_list[16]['summary']
        assert "2020-09-22T21:55:00.000000-0400" == event_list[17]['start']
        assert "summary9" == event_list[17]['summary']
        assert "2020-09-29T21:55:00.000000-0400" == event_list[18]['start']
        assert "summary9" == event_list[18]['summary']

        assert "2020-09-16T02:00:00.000000-0400" == event_list[19]['start']
        assert "summary10" == event_list[19]['summary']
        assert "2020-09-23T02:00:00.000000-0400" == event_list[20]['start']
        assert "summary10" == event_list[20]['summary']

        assert "2020-09-16T21:55:00.000000-0400" == event_list[21]['start']
        assert "summary12" == event_list[21]['summary']
        assert "2020-09-23T21:55:00.000000-0400" == event_list[22]['start']
        assert "summary12" == event_list[22]['summary']

        assert "2020-09-16T20:00:00.000000-0400" == event_list[23]['start']
        assert "summary13" == event_list[23]['summary']
        assert "2020-09-23T20:00:00.000000-0400" == event_list[24]['start']
        assert "summary13" == event_list[24]['summary']

    @pytest.mark.parametrize('fileName', ['issue22.ics'])
    def test_issue_twenty_two_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-01-31T23:59:59"), True)
        assert event_list is not None
        assert 1 == len(event_list)
        for event in event_list:
            assert "Betws-y-Coed (Caravan Holiday)" == event['summary']
            assert "Betws-y-Coed (Caravan Holiday)" == event['description']

    @pytest.mark.parametrize('fileName', ['issue22.ics'])
    def test_issue_twenty_two_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2020-01-01T00:00:00"), dtparser.parse("2020-01-31T23:59:59"), True)
        assert event_list is not None
        assert 1 == len(event_list)
        for event in event_list:
            assert "Betws-y-Coed (Caravan Holiday)" == event['summary']
            assert "Betws-y-Coed (Caravan Holiday)" == event['description']

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

    # ics parser fails on floating events
    @pytest.mark.xfail()
    @pytest.mark.parametrize('fileName', ['issue36.ics'])
    def test_issue_thirty_six_for_ics(self, ics_parser, calendar_data):
        event_list = ics_parser.get_event_list(calendar_data, dtparser.parse("2021-09-16T00:00:00"), dtparser.parse("2021-09-16T23:59:59"), True)
        assert event_list is not None
        assert 1 == len(event_list)
        # TODO Make these checks generic, and ensure the time comparison isn't a string!
        for event in event_list:
            assert "2021-09-16T21:00:00-04:00" == event['start']
            assert "2021-12-12T22:45:00-04:00" == event['end']

    # icalevents parser fails on floating events
    @pytest.mark.xfail()
    @pytest.mark.parametrize('fileName', ['issue36.ics'])
    def test_issue_thirty_six_for_icalevents(self, icalevents_parser, calendar_data):
        event_list = icalevents_parser.get_event_list(calendar_data, dtparser.parse("2021-09-16T00:00:00"), dtparser.parse("2021-09-16T23:59:59"), True)
        assert event_list is not None
        assert 1 == len(event_list)
        # TODO Make these checks generic, and ensure the time comparison isn't a string!
        for event in event_list:
            assert "2021-09-16T21:00:00.000000-0400" == event['start']
            assert "2021-09-16T22:45:00.000000-0400" == event['end']

