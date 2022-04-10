"""Test the CalendarData class."""
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.request import HTTPHandler, build_opener, install_opener
from urllib.response import addinfourl

from dateutil import parser as dtparser

from custom_components.ics_calendar.calendardata import CalendarData

BINARY_CALENDAR_DATA = b"calendar data"
BINARY_CALENDAR_DATA_2 = b"2 calendar data"
CALENDAR_DATA = "calendar data"
CALENDAR_DATA_2 = "2 calendar data"
CALENDAR_NAME = "TESTcalendar"
TEST_URL = "http://127.0.0.1/test/allday.ics"


def set_calendar_data(calendar_data: CalendarData, data: str):
    """Set _calendarData for the passed CalendarData object."""
    calendar_data._calendar_data = data  # pylint: disable=W0212


def mock_response(req, data: str):
    """Return an HttpResponse object with the given data."""
    resp = addinfourl(BytesIO(data), "message", req.get_full_url())
    resp.code = 200
    resp.msg = "OK"
    return resp


class MockHTTPHandlerContentTooShortError(HTTPHandler):
    """Mock HTTPHandler with a ContentTooShortError."""

    def http_open(self, req):
        """Provide http_open to raise exception."""
        raise ContentTooShortError("Expected 1000 bytes", CALENDAR_DATA)


class MockHTTPHandlerHTTPError(HTTPHandler):
    """Mock HTTPHandler with an HTTPError."""

    def http_open(self, req):
        """Provide http_open to raise exception."""
        raise HTTPError(404, "not found", None, None, None)


class MockHTTPHandlerURLError(HTTPHandler):
    """Mock HTTPHandler with an URLError."""

    def http_open(self, req):
        """Provide http_open to raise exception."""
        raise URLError("bad url")


class MockHTTPHandlerError(HTTPHandler):
    """Mock HTTPHandler with a BaseException."""

    def http_open(self, req):
        """Provide http_open to raise exception."""
        raise BaseException("Unknown error")


class MockHTTPHandler(HTTPHandler):
    """Mock HTTPHandler that returns BINARY_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to rreturn BINARY_CALENDAR_DATA."""
        return mock_response(req, BINARY_CALENDAR_DATA)


class MockHTTPHandler2(HTTPHandler):
    """Mock HTTPHandler that returns BINARY_CALENDAR_DATA_2."""

    def http_open(self, req):
        """Provide http_open to rreturn BINARY_CALENDAR_DATA_2."""
        return mock_response(req, BINARY_CALENDAR_DATA_2)


class TestCalendarData:
    """Test the CalendarData class."""

    def test_set_username_and_password(self, logger):
        """Test setting user name and password.

        This doesn't do much, since set_user_name_and_password has no failure
        conditions.  We could test that it actually does what it's supposed to
        do, except that means checking the implementation.
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        calendar_data.set_user_name_password("username", "password")

    def test_get(self, logger):
        """Test get method retrieves cached data."""
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        set_calendar_data(calendar_data, CALENDAR_DATA)
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar_ContentTooShortError(self, logger):
        """Test that None is cached for ContentTooShortError.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerContentTooShortError)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

    def test_download_calendar_HTTPError(self, logger):
        """Test that None is cached for HTTPError.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerHTTPError)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

    def test_download_calendar_URLError(self, logger):
        """Test that None is cached for URLError.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerURLError)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

    def test_download_calendar_Error(self, logger):
        """Test that None is cached for BaseException.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerError)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    def test_get_returns_new_data(self, mock_hanow, logger):
        """Test that get causes downloads if enough time has passed."""
        mock_hanow.side_effect = [
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:05:05"),
        ]
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        install_opener(opener)
        assert calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

        opener = build_opener(MockHTTPHandler2)
        install_opener(opener)
        assert calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA_2

    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    def test_get_too_quickly_returns_old_data(self, mock_hanow, logger):
        """Test that get does not download if not enough time has passed."""
        mock_hanow.side_effect = [
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:04:59"),
        ]
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        install_opener(opener)
        assert calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

        opener = build_opener(MockHTTPHandler2)
        install_opener(opener)
        assert not calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA
