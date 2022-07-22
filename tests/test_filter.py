"""Test the Filter class."""
import pytest
from homeassistant.components.calendar import CalendarEvent

from custom_components.ics_calendar.filter import Filter


@pytest.fixture()
def calendar_event():
    return CalendarEvent(
        summary="summary",
        start="start",
        end="start",
        location="location",
        description="description",
    )


class TestFilter:
    """Test the Filter class."""

    def test_filter_empty(self):
        """Test setting user agent"""
        filt = Filter("", "")
        assert filt.filter("summary", "description") is True

    def test_filter_event_empty(self, calendar_event):
        """Test setting user agent"""
        filt = Filter("", "")
        assert filt.filter_event(calendar_event) is True

    def test_filter_string_exclude_description(self):
        """Test setting user agent"""
        filt = Filter("['crip']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_string_exclude_passes(self):
        """Test setting user agent"""
        filt = Filter("['blue']", "")
        assert filt.filter("summary", "description") is True

    def test_filter_string_exclude(self):
        """Test setting user agent"""
        filt = Filter("['um']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_string_exclude_is_not_case_sensitive(self):
        """Test setting user agent"""
        filt = Filter("['um']", "")
        assert filt.filter("SUMMARY", "description") is False

    def test_filter_string_exclude_but_string_include(self):
        """Test setting user agent"""
        filt = Filter("['um']", "['crip']")
        assert filt.filter("summary", "description") is True

    def test_filter_string_exclude_but_regex_include(self):
        """Test setting user agent"""
        filt = Filter("['um']", "['/crip/']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude(self):
        """Test setting user agent"""
        filt = Filter("['/um/']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_regex_exclude_but_string_include(self):
        """Test setting user agent"""
        filt = Filter("['/um/']", "['crip']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude_but_regex_include(self):
        """Test setting user agent"""
        filt = Filter("['/um/']", "['/crip/']")
        assert filt.filter("summary", "description") is True

    def test_filter_regex_exclude_ignore_case(self):
        """Test setting user agent"""
        filt = Filter("['/UM/i']", "")
        assert filt.filter("summary", "description") is False

    def test_filter_regex_exclude_ignore_case_multiline(self):
        """Test setting user agent"""
        filt = Filter("['/CRiPT-$/im']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_ignore_case_multiline_dotall(self):
        """Test setting user agent"""
        filt = Filter("['/cript-.ion/sim']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_multiline(self):
        """Test setting user agent"""
        filt = Filter("['/cript-$/m']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_multiline_dotall(self):
        """Test setting user agent"""
        filt = Filter("['/cript-.ion/ms']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )

    def test_filter_regex_exclude_dotall(self):
        """Test setting user agent"""
        filt = Filter("['/cript-./s']", "")
        assert (
            filt.filter(
                "summary",
                """descript-
ion""",
            )
            is False
        )
