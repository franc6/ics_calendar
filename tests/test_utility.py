"""Test utility.py."""
from datetime import date, datetime

from custom_components.ics_calendar.utility import compare_event_dates

# from unittest.mock import Mock


# import pytest

janOneTwelveThirty = datetime(2022, 1, 1, 12, 30, 0).astimezone()
janOneTwelveThirtyFive = datetime(2022, 1, 1, 12, 35, 0).astimezone()
janOneTwelveFourty = datetime(2022, 1, 1, 12, 40, 0).astimezone()
janOneThirteenThirty = datetime(2022, 1, 1, 13, 30, 0).astimezone()
janOneFourteenThirty = datetime(2022, 1, 1, 14, 30, 0).astimezone()
janTwoTwelveThirty = datetime(2022, 1, 2, 12, 30, 0).astimezone()
janTwoThirteenThirty = datetime(2022, 1, 2, 13, 30, 0).astimezone()
febOneTwelveThirty = datetime(2022, 2, 1, 12, 30, 0).astimezone()
janOne = date(2022, 1, 1)
janOne = date(2022, 1, 1)
janTwo = date(2022, 1, 2)
janTwo = date(2022, 1, 2)
janThree = date(2022, 1, 3)
febOne = date(2022, 2, 1)


class TestUtility:
    """Test the Filter class."""

    def test_compare_event_dates_newer(self) -> None:
        """Test that Jan 2@12:30 is newer than Jan 1@12:30."""
        assert (
            compare_event_dates(
                febOneTwelveThirty,
                janTwoThirteenThirty,
                janTwoTwelveThirty,
                False,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
            )
            is True
        )

    def test_compare_event_dates_older(self) -> None:
        """Test that Jan 1@12:30 is older than Jan 2@12:30."""
        assert (
            compare_event_dates(
                febOneTwelveThirty,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
                janTwoThirteenThirty,
                janTwoTwelveThirty,
                False,
            )
            is False
        )

    def test_compare_event_dates_newer_all_day(self) -> None:
        """Test that Jan 1 is older than Jan 2."""
        assert (
            compare_event_dates(
                febOneTwelveThirty, janTwo, janTwo, True, janOne, janOne, True
            )
            is True
        )

    def test_compare_event_dates_older_all_day(self) -> None:
        """Test that Jan 1 is older than Jan 2."""
        assert (
            compare_event_dates(
                febOneTwelveThirty, janOne, janOne, True, janTwo, janTwo, True
            )
            is False
        )

    def test_compare_event_dates_all_day_newer_than_not_all_day(self) -> None:
        """Test that all day Jan 2 is newer than Jan 1@12:30."""
        assert (
            compare_event_dates(
                febOneTwelveThirty,
                janThree,
                janTwo,
                True,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
            )
            is True
        )

    def test_compare_event_dates_all_day_older_than_not_all_day(self) -> None:
        """Test that all day Jan 1 is older than Jan 2@12:30."""
        assert (
            compare_event_dates(
                febOneTwelveThirty,
                janTwo,
                janOne,
                True,
                janTwoThirteenThirty,
                janTwoTwelveThirty,
                False,
            )
            is False
        )

    def test_compare_event_dates_not_all_day_newer_than_all_day(self) -> None:
        """Test that Jan 1@12:30 is newer than Jan 1 all day."""
        assert (
            compare_event_dates(
                datetime.now(),
                janTwoThirteenThirty,
                janTwoTwelveThirty,
                False,
                janOne,
                janTwo,
                True,
            )
            is True
        )

    def test_compare_event_dates_not_all_day_older_than_all_day(self) -> None:
        """Test that Jan 1@12:30 is older than Jan 2 all day."""
        assert (
            compare_event_dates(
                datetime.now(),
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
                janTwo,
                janThree,
                True,
            )
            is False
        )

    def test_compare_event_dates_newer_same_end_later_start(self) -> None:
        """Test that Jan 1@12:35 is newer than Jan 1@12:30 for same end."""
        assert (
            compare_event_dates(
                febOneTwelveThirty,
                janOneThirteenThirty,
                janOneTwelveThirtyFive,
                False,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
            )
            is True
        )

    def test_compare_event_dates_older_same_end_earlier_start(self) -> None:
        """Test that Jan 1@12:30 is older than Jan 1@12:35 for same end."""
        assert (
            compare_event_dates(
                febOneTwelveThirty,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
                janOneThirteenThirty,
                janOneTwelveThirtyFive,
                False,
            )
            is False
        )

    def test_compare_event_dates_newer_not_all_day_during(self) -> None:
        """Test that Jan 1@12:30 is newer than Jan 1 all day."""
        assert (
            compare_event_dates(
                janOneTwelveThirtyFive,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
                janTwo,
                janOne,
                True,
            )
            is True
        )

    def test_compare_event_dates_older_not_all_day_during(self) -> None:
        """Test that Jan 1 all day is older than Jan 1@12:30."""
        assert (
            compare_event_dates(
                janOneTwelveThirtyFive,
                janTwo,
                janOne,
                True,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
            )
            is False
        )

    def test_compare_event_dates_older_earlier_end_later_start(self) -> None:
        """Test that Jan 1@12:30-1:30 is newer than Jan1@12:30-12:35."""
        assert (
            compare_event_dates(
                janOneTwelveThirtyFive,
                janOneThirteenThirty,
                janOneTwelveThirty,
                True,
                janOneTwelveThirtyFive,
                janOneTwelveThirty,
                False,
            )
            is False
        )

    def test_compare_event_dates_older_earlier_end_later_start2(self) -> None:
        """Test that Jan 1@12:30-1:30 is newer than Jan1@12:30-12:35."""
        assert (
            compare_event_dates(
                janOneTwelveThirtyFive,
                janOneTwelveThirtyFive,
                janOneTwelveThirty,
                True,
                janOneThirteenThirty,
                janOneTwelveThirty,
                False,
            )
            is False
        )


# TODO: all day v not-all-day events, for overlapping times
# A not-all-day event should be "newer" than an all day event if now is during
# the not-all-day event
# An all day event should be "nweer" than an all day event if now is NOT during
# the not-all-day event
