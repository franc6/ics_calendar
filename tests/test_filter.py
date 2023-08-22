"""Test the Filter class."""
import pytest
from dateutil import parser as dtparser
from homeassistant.components.calendar import CalendarEvent

from custom_components.ics_calendar.filter import Filter


@pytest.fixture()
def calendar_event() -> CalendarEvent:
    """Fixture to return a CalendarEvent."""
    return CalendarEvent(
        summary="summary",
        start=dtparser.parse("2020-01-01T0:00:00").astimezone(),
        end=dtparser.parse("2020-01-01T0:00:00").astimezone(),
        location="location",
        description="description",
    )


class TestFilter:
    """Test the Filter class."""

    def test_filter_empty(self) -> None:
        """Test that an empty filter works."""
        filt = Filter("", "")
        assert filt.filter("summary", "description") is True

    def test_filter_event_empty(self, calendar_event: CalendarEvent) -> None:
        """Test that an empty filter works on an event."""
        filt = Filter("", "")
        assert filt.filter_event(calendar_event) is True

    def test_filter_string_exclude_description(self) -> None:
        """Test that string exclude works on description."""
        filt = Filter("['crip']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_string_exclude_passes(self) -> None:
        """Test that string exclude works if string not found."""
        filt = Filter("['blue']", "")
        assert filt.filter("summary", "description") is True

    def test_filter_string_exclude(self) -> None:
        """Test that string exclude works on summary."""
        filt = Filter("['um']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_string_exclude_is_not_case_sensitive(self) -> None:
        """Test that string exclude filter is not case-sensitive."""
        filt = Filter("['um']", "")
        assert filt.filter("SUMMARY", "description") is False

    def test_filter_string_exclude_but_string_include(self) -> None:
        """Test that string exclude filter with including string works."""
        filt = Filter("['um']", "['crip']")
        assert filt.filter("summary", "description") is True

    def test_filter_string_exclude_but_regex_include(self) -> None:
        """Test that string exclude filter with including regex works."""
        filt = Filter("['um']", "['/crip/']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude(self) -> None:
        """Test that regex exclude filter works."""
        filt = Filter("['/um/']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_regex_exclude_but_string_include(self) -> None:
        """Test that regex exclude filter with including string works."""
        filt = Filter("['/um/']", "['crip']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude_but_regex_include(self) -> None:
        """Test that regex exclude filter with including regex works."""
        filt = Filter("['/um/']", "['/crip/']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude_ignore_case(self) -> None:
        """Test that regex exclude filter with ignore case works."""
        filt = Filter("['/UM/i']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_regex_exclude_ignore_case_multiline(self) -> None:
        """Test that regex exclude filter with ignore case, multi-line works."""
        filt = Filter("['/CRiPT-$/im']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_ignore_case_multiline_dotall(self) -> None:
        """Test that regex exclude filter with all options works."""
        filt = Filter("['/cript-.ion/sim']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_multiline(self) -> None:
        """Test that regex exclude filter with multi-line works."""
        filt = Filter("['/cript-$/m']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
    ion""",
            )
            is False
        )

    def test_filter_regex_exclude_multiline_dotall(self) -> None:
        """Test that regex exclude filter with multi-line dotall works."""
        filt = Filter("['/cript-.ion/ms']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_dotall(self) -> None:
        """Test that regex exclude filter with dotall works."""
        filt = Filter("['/cript-./s']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_with_description_none(self) -> None:
        """Test that filter works if description is None."""
        filt = Filter("['exclude']", "['include']")
        assert filt.filter("summary", None) is True
