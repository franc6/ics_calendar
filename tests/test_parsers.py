import pytest
from dateutil import parser as dtparser
import ics


class TestParsers:
    @pytest.mark.parametrize(
        "which_parser",
        [
            # Issue 6 is a problem for ics still!
            pytest.param(
                "ics_parser",
                # ICS 0.8 uses a different class hierarchy for ParseError
                # marks=pytest.mark.xfail(raises=ics.contentline.container.ParseError)
                marks=pytest.mark.xfail(raises=ics.grammar.parse.ParseError),
            ),
            "icalevents_parser",
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue6.ics"])
    def test_issue_six(self, parser, calendar_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2020-01-01T00:00:00"),
            dtparser.parse("2020-01-31T23:59:59"),
            False,
        )
        pytest.helpers.assert_event_list_size(1, event_list)

    @pytest.mark.xfail()
    @pytest.mark.parametrize(
        "which_parser",
        # ics parser doesn't handle recurring events
        [pytest.param("ics_parser", marks=pytest.mark.xfail), "icalevents_parser"],
    )
    @pytest.mark.parametrize(
        "fileName",
        ["issue8.ics"],
        indirect=True,
    )
    def test_issue_eight(self, parser, calendar_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2020-01-01T00:00:00"),
            dtparser.parse("2020-06-15T23:59:59"),
            True,
        )
        assert event_list is not None
        pytest.helpers.assert_event_list_size(2, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        # ics parser doesn't handle recurring events
        [pytest.param("ics_parser", marks=pytest.mark.xfail), "icalevents_parser"],
    )
    @pytest.mark.parametrize("fileName", ["issue17.ics"])
    def test_issue_seventeen(self, parser, calendar_data, expected_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2020-09-14T00:00:00-0400"),
            dtparser.parse("2020-09-29T23:59:59-0400"),
            True,
        )
        pytest.helpers.assert_event_list_size(25, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        ["ics_parser", "icalevents_parser"],
    )
    @pytest.mark.parametrize("fileName", ["issue22.ics"])
    def test_issue_twenty_two(self, parser, calendar_data, expected_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2020-01-01T00:00:00"),
            dtparser.parse("2020-01-31T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        ["ics_parser", "icalevents_parser"],
    )
    @pytest.mark.parametrize("fileName", ["issue34.ics"])
    def test_issue_thirty_four(self, parser, calendar_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2021-01-01T00:00:00"),
            dtparser.parse("2021-12-31T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(123, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            # ics parser fails on floating events
            pytest.param("ics_parser", marks=pytest.mark.xfail),
            # icalevents parser fails on floating events
            pytest.param("icalevents_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue36.ics"])
    def test_issue_thirty_six(self, parser, calendar_data, expected_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2021-09-16T00:00:00"),
            dtparser.parse("2021-09-16T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)
