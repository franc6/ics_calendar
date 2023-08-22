"""Test the parsers, especially for past issues."""
from unittest.mock import Mock

import ics
import pytest
from dateutil import parser as dtparser
from homeassistant.util import dt as hadt


class TestParsers:
    """Test the parsers, especially for past issues."""

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("file_name", ["test_parsers.py"])
    def test_not_a_calendar(self, parser, calendar_data):
        """Test parsing something that is not a calendar."""
        with pytest.raises(Exception):
            parser.set_content(calendar_data)
        with pytest.raises(Exception):
            parser.set_content(None)
        with pytest.raises(Exception):
            parser.set_content("")

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    def test_no_content(self, parser):
        """Test parsing a calendar including all day events."""
        event_list = parser.get_event_list(
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-31T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(0, event_list)

        assert (
            parser.get_current_event(
                True, dtparser.parse("2022-01-01T00:00:00"), 31
            )
            is None
        )

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            # ics_parser fails due to time zone problems
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("file_name", ["allday.ics"])
    def test_all_day(self, parser, calendar_data, expected_data):
        """Test parsing a calendar including all day events."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
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
    @pytest.mark.parametrize("file_name", ["allday.ics"])
    def test_no_all_day(self, parser, calendar_data):
        """Test parsing a calendar excluding all day events."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-31T23:59:59"),
            False,
        )
        pytest.helpers.assert_event_list_size(4, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("file_name", ["allday.ics"])
    def test_no_all_day_current(self, parser, calendar_data):
        """Test get_current_event for a calendar excluding all day events."""
        parser.set_content(calendar_data)
        event = parser.get_current_event(
            False, dtparser.parse("2022-01-01T00:00:00"), 31
        )
        assert event is not None

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("file_name", ["allday.ics"])
    def test_no_all_day_current_filtered(self, parser, calendar_data):
        """Test get_current_event for a calendar excluding all day events."""
        parser.set_content(calendar_data)
        filt = Mock()
        filt.filter.return_value = False
        parser.set_filter(filt)
        event = parser.get_current_event(
            False, dtparser.parse("2022-01-01T00:00:00"), 31
        )
        assert event is None

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            pytest.param(
                "ics_parser",
                # ICS 0.8 uses a different class hierarchy for ParseError
                # marks=pytest.mark.xfail(raises=ics.contentline.container.ParseError)
                marks=pytest.mark.xfail(raises=ics.grammar.parse.ParseError),
            ),
        ],
    )
    @pytest.mark.parametrize("file_name", ["issue6.ics"])
    def test_issue_six(self, parser, calendar_data):
        """Test if still fixed, issue 6."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
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
    @pytest.mark.parametrize("file_name", ["issue8.ics"])
    def test_issue_eight(self, parser, calendar_data):
        """Test if still fixed, issue 8."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
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
    @pytest.mark.parametrize("file_name", ["issue17.ics"])
    def test_issue_seventeen(self, parser, calendar_data, expected_data):
        """Test if still fixed, issue 17."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
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
    @pytest.mark.parametrize("file_name", ["issue22.ics"])
    def test_issue_twenty_two(self, parser, calendar_data, expected_data):
        """Test if still fixed, issue 22."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
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
    @pytest.mark.parametrize("file_name", ["issue34.ics"])
    def test_issue_thirty_four(self, parser, calendar_data):
        """Test if still fixed, issue 34."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2021-01-01T00:00:00"),
            dtparser.parse("2021-12-31T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(123, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("file_name", ["issue34.ics"])
    def test_with_exclude_filter(self, parser, calendar_data):
        """Test if still fixed, issue 34."""
        parser.set_content(calendar_data)
        filt = Mock()
        filt.filter_event.return_value = False
        parser.set_filter(filt)
        event_list = parser.get_event_list(
            dtparser.parse("2021-01-01T00:00:00"),
            dtparser.parse("2021-12-31T23:59:59"),
            True,
        )
        pytest.helpers.assert_event_list_size(0, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            # ics parser fails on floating events before 0.8.0
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("file_name", ["issue36.ics"])
    def test_issue_thirty_six(self, parser, calendar_data, expected_data):
        """Test if still fixed, issue 36."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
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
    @pytest.mark.parametrize("file_name", ["issue43.ics"])
    def test_issue_forty_three_two_days(
        self, parser, calendar_data, expected_data
    ):
        """Test if still fixed, issue 43."""
        now = dtparser.parse("2022-02-28T06:00:00-04:00")
        parser.set_content(calendar_data)
        current_event = parser.get_current_event(True, now, 2)
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
    @pytest.mark.parametrize("file_name", ["issue43.ics"])
    @pytest.mark.parametrize("expected_name", ["issue43-14.ics"])
    def test_issue_forty_three_fourteen_days(
        self, parser, calendar_data, expected_data
    ):
        """Test if still fixed, issue 43."""
        now = dtparser.parse("2022-03-01T06:00:00-04:00")
        parser.set_content(calendar_data)
        current_event = parser.get_current_event(True, now, 14)
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
    @pytest.mark.parametrize("file_name", ["issue43.ics"])
    def test_issue_forty_three_seven_days(self, parser, calendar_data):
        """Test if still fixed, issue 43."""
        now = dtparser.parse("2022-03-01T06:00:00-05:00")
        parser.set_content(calendar_data)
        current_event = parser.get_current_event(True, now, 7)
        assert current_event is None

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            "ics_parser",
        ],
    )
    @pytest.mark.parametrize("file_name", ["issue45.ics"])
    def test_issue_forty_five(self, parser, calendar_data, expected_data):
        """Test if still fixed, issue 45."""
        now = dtparser.parse("2022-02-28T06:00:00-05:00")
        parser.set_content(calendar_data)
        current_event = parser.get_current_event(True, now, 1)
        event_list = [current_event]
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)

    @pytest.mark.parametrize(
        "which_parser",
        [
            "rie_parser",
            # ics parser fails on floating events before 0.8.0
            pytest.param("ics_parser", marks=pytest.mark.xfail),
        ],
    )
    @pytest.mark.parametrize("file_name", ["issue48.ics"])
    def test_issue_forty_eight(self, parser, calendar_data, expected_data):
        """Test if still fixed, issue 48."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2021-09-16T00:00:00"),
            dtparser.parse("2021-09-17T23:59:59"),
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
    @pytest.mark.parametrize("file_name", ["positive_offset.ics"])
    def test_positive_offset_hours(self, parser, calendar_data, expected_data):
        """Test if offset_hours works."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2021-09-16T00:00:00"),
            dtparser.parse("2021-09-17T23:59:59"),
            True,
            2,
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
    @pytest.mark.parametrize("file_name", ["negative_offset.ics"])
    def test_negative_offset_hours(self, parser, calendar_data, expected_data):
        """Test if offset_hours works."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2021-09-16T00:00:00"),
            dtparser.parse("2021-09-17T23:59:59"),
            True,
            -4,
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
    @pytest.mark.parametrize("file_name", ["positive_offset_all_day.ics"])
    def test_positive_offset_hours_all_day(
        self, parser, calendar_data, expected_data
    ):
        """Test if offset_hours works."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2021-09-16T00:00:00"),
            dtparser.parse("2021-09-18T23:59:59"),
            True,
            2,
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
    @pytest.mark.parametrize("file_name", ["negative_offset_all_day.ics"])
    def test_negative_offset_hours_all_day(
        self, parser, calendar_data, expected_data
    ):
        """Test if offset_hours works."""
        parser.set_content(calendar_data)
        event_list = parser.get_event_list(
            dtparser.parse("2021-09-15T00:00:00"),
            dtparser.parse("2021-09-17T23:59:59"),
            True,
            -4,
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
    @pytest.mark.parametrize(
        "set_tz", ["utc", "chicago", "baghdad"], indirect=True
    )
    @pytest.mark.parametrize("file_name", ["issue92.ics"])
    def test_issue_ninety_two(
        self, parser, set_tz, calendar_data, expected_data
    ):
        """Test if still fixed, issue 92."""
        now = hadt.as_local(dtparser.parse("2022-12-30T06:00:00"))
        parser.set_content(calendar_data)
        current_event = parser.get_current_event(True, now, 5)
        event_list = [current_event]
        pytest.helpers.assert_event_list_size(1, event_list)
        pytest.helpers.compare_event_list(expected_data, event_list)
