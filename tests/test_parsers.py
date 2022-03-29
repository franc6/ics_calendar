import pytest
from dateutil import parser as dtparser
import ics


class TestParsers:
    # Test all day events, make sure time and zone are corret
    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            # ics_parser fails due to time zone problems
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("fileName", ["allday.ics"])
    def test_all_day(self, parser, calendar_data, expected_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-31T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(11, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)

    # Test skipping all day events
    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            # ics_parser fails due to time zone problems
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("fileName", ["allday.ics"])
    def test_no_all_day(self, parser, calendar_data):
        event_list = parser.get_event_list(
            calendar_data,
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-31T23:59:59"),
            False,
        )
        pytest.helpers.assert_event_list_size(4, event_list)

    # TODO: Test get_current_event, make sure time and zone are correct
    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            pytest.param(
                "ics_parser",
                # ICS 0.8 uses a different class hierarchy for ParseError
                # marks=pytest.mark.xfail(raises=ics.contentline.container.ParseError)
                marks=pytest.mark.xfail(raises=ics.grammar.parse.ParseError)
            ),
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

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            # ics parser doesn't handle recurring events
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue8.ics"])
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
        [
            "rie_parser",
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
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
        [
            "rie_parser",
            "ics_parser",
        ],
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
        [
            "rie_parser",
            "ics_parser",
        ],
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
            "rie_parser",
            # ics parser fails on floating events before 0.8.0
            pytest.param("ics_parser", marks=pytest.mark.xfail),
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

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue45.ics"])
    def test_issue_forty_three_two_days(self, parser, calendar_data, expected_data):
        now = dtparser.parse("2022-02-28T06:00:00-05:00")
        current_event = parser.get_current_event(calendar_data, True, now, 2)
        event_list = [current_event]
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue43.ics"])
    def test_issue_forty_three_fourteen_days(self, parser, calendar_data, expected_data):
        now = dtparser.parse("2022-03-01T06:00:00-05:00")
        current_event = parser.get_current_event(calendar_data, True, now, 14)
        event_list = [current_event]
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue43.ics"])
    def test_issue_forty_three_seven_days(self, parser, calendar_data):
        now = dtparser.parse("2022-03-01T06:00:00-05:00")
        current_event = parser.get_current_event(calendar_data, True, now, 7)
        assert current_event is None

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("fileName", ["issue45.ics"])
    def test_issue_forty_five(self, parser, calendar_data, expected_data):
        now = dtparser.parse("2022-02-28T06:00:00-05:00")
        current_event = parser.get_current_event(calendar_data, True, now, 1)
        event_list = [current_event]
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)
