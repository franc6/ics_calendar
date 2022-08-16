"""Test the Filter class."""
import pytest
from homeassistant.components.calendar import CalendarEvent

from custom_components.ics_calendar.filter import Filter


@pytest.fixture()
def calendar_event() -> CalendarEvent:
    return CalendarEvent(
        summary="summary",
        start="start",
        end="start",
        location="location",
        description="description",
    )


class TestFilter:
    """Test the Filter class."""

    def test_filter_empty(self) -> None:
        filt = Filter("", "")
        assert filt.filter("summary", "description") is True

    def test_filter_event_empty(self, calendar_event: CalendarEvent) -> None:
        filt = Filter("", "")
        assert filt.filter_event(calendar_event) is True

    def test_filter_string_exclude_description(self) -> None:
        filt = Filter("['crip']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_string_exclude_passes(self) -> None:
        filt = Filter("['blue']", "")
        assert filt.filter("summary", "description") is True

    def test_filter_string_exclude(self) -> None:
        filt = Filter("['um']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_string_exclude_is_not_case_sensitive(self) -> None:
        filt = Filter("['um']", "")
        assert filt.filter("SUMMARY", "description") is False

    def test_filter_string_exclude_but_string_include(self) -> None:
        filt = Filter("['um']", "['crip']")
        assert filt.filter("summary", "description") is True

    def test_filter_string_exclude_but_regex_include(self) -> None:
        filt = Filter("['um']", "['/crip/']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude(self) -> None:
        filt = Filter("['/um/']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_regex_exclude_but_string_include(self) -> None:
        filt = Filter("['/um/']", "['crip']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude_but_regex_include(self) -> None:
        filt = Filter("['/um/']", "['/crip/']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude_ignore_case(self) -> None:
        filt = Filter("['/UM/i']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_regex_exclude_ignore_case_multiline(self) -> None:
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
        filt = Filter("['exclude']", "['include']")
        assert filt.filter("summary", None) is True
