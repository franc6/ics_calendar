"""Test the CalendarData class."""
import email
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
UTF8_BOM_CALENDAR_DATA = (
    b"\xef\xbb\xbf\x63\x61\x6c\x65\x6e\x64\x61\x72\x20\x64\x61\x74\x61"
)
UTF16_BOM_BE_CALENDAR_DATA = (
    b"\xfe\xff\x00\x63\x00\x61\x00\x6c\x00\x65\x00\x6e\x00\x64"
    b"\x00\x61\x00\x72\x00\x20\x00\x64\x00\x61\x00\x74\x00\x61"
)
UTF16_BOM_LE_CALENDAR_DATA = (
    b"\xff\xfe\x63\x00\x61\x00\x6c\x00\x65\x00\x6e\x00\x64\x00"
    b"\x61\x00\x72\x00\x20\x00\x64\x00\x61\x00\x74\x00\x61\x00"
)
BAD_UTF_CALENDAR_DATA = b"\xf0\xa4\xad"
GZIP_CALENDAR_DATA = (
    b"\x1f\x8b\x08\x00\x5b\x41\x61\x63\x02\x03"  # GZIP header
    b"\x4b\x4e\xcc\x49\xcd\x4b\x49\x2c\x52\x48\x49\x2c\x49\x04\x00"
    b"\x29\x07\xe7\x84"  # CRC-32
    b"\x0d\x00\x00\x00"  # uncompressed size
)
BAD_GZIP_CALENDAR_DATA = (
    b"\x2f\x8b\x08\x00\x5b\x41\x61\x63\x02\x03"  # GZIP header
    b"\x4b\x4e\xcc\x49\xcd\x4b\x49\x2c\x52\x48\x49\x2c\x49\x04\x00"
    b"\x29\x07\xe7\x84"  # CRC-32
    b"\x0d\x00\x00\x00"  # uncompressed size
)
BAD_DEFLATE_CALENDAR_DATA = (
    b"\x1f\x8b\x08\x00\x5b\x41\x61\x63\x02\x03"  # GZIP header
    b"\x4b\x4e\xcc\x49\xcd\x4b\x49\x2c\x52\x48\x49\x2c\x49\xf4\x00"
    b"\x29\x07\xe7\x84"  # CRC-32
    b"\x0d\x00\x00\x00"  # uncompressed size
)

TEST_URL = "http://127.0.0.1/test/allday.ics"


def set_calendar_data(calendar_data: CalendarData, data: str):
    """Set _calendarData for the passed CalendarData object."""
    calendar_data._calendar_data = data  # pylint: disable=W0212


def mock_response(req, data: str, encoding: str = None):
    """Return an HttpResponse object with the given data."""
    # resp = addinfourl(BytesIO(data), "message", req.get_full_url())
    header_string = """Content-type: application/octet-stream
Content-length: {len(data)}
"""
    if encoding is not None:
        header_string += f"Content-Encoding: {encoding}\n"

    resp = addinfourl(
        BytesIO(data),
        email.message_from_string(header_string),
        req.get_full_url(),
        200,
    )
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
        """Provide http_open to return BINARY_CALENDAR_DATA."""
        return mock_response(req, BINARY_CALENDAR_DATA)


class MockHTTPHandlerUTF8BOM(HTTPHandler):
    """Mock HTTPHandler that returns UTF8_BOM_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return UTF8_BOM_CALENDAR_DATA."""
        return mock_response(req, UTF8_BOM_CALENDAR_DATA)


class MockHTTPHandlerUTF16BOMBE(HTTPHandler):
    """Mock HTTPHandler that returns UTF16_BOM_BE_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return UTF16_BOM_BE_CALENDAR_DATA."""
        return mock_response(req, UTF16_BOM_BE_CALENDAR_DATA)


class MockHTTPHandlerUTF16BOMLE(HTTPHandler):
    """Mock HTTPHandler that returns UTF16_BOM_LE_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return UTF16_BOM_LE_CALENDAR_DATA."""
        return mock_response(req, UTF16_BOM_LE_CALENDAR_DATA)


class MockHTTPHandlerBadUTF(HTTPHandler):
    """Mock HTTPHandler that returns BAD_UTF_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return BAD_UTF_CALENDAR_DATA."""
        return mock_response(req, BAD_UTF_CALENDAR_DATA)


class MockHTTPGzipHandler(HTTPHandler):
    """Mock HTTPHandler that returns GZIP_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return GZIP_CALENDAR_DATA."""
        return mock_response(req, GZIP_CALENDAR_DATA, "gzip")


class MockHTTPGzipHandlerBadGzip(HTTPHandler):
    """Mock HTTPHandler that returns BAD_GZIP_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return BAD_GZIP_CALENDAR_DATA."""
        return mock_response(req, BAD_GZIP_CALENDAR_DATA, "gzip")


class MockHTTPGzipHandlerBadDeflate(HTTPHandler):
    """Mock HTTPHandler that returns BAD_DEFLATE_CALENDAR_DATA."""

    def http_open(self, req):
        """Provide http_open to return BAD_DEFLATE_CALENDAR_DATA."""
        return mock_response(req, BAD_DEFLATE_CALENDAR_DATA, "gzip")


class MockHTTPHandler2(HTTPHandler):
    """Mock HTTPHandler that returns BINARY_CALENDAR_DATA_2."""

    def http_open(self, req):
        """Provide http_open to return BINARY_CALENDAR_DATA_2."""
        return mock_response(req, BINARY_CALENDAR_DATA_2)


class TestCalendarData:
    """Test the CalendarData class."""

    def test_set_headers_none(self, logger):
        """Test set_headers without user name, password, or user agent."""
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        calendar_data.set_headers("", "", "")

    def test_set_user_agent(self, logger):
        """Test setting user agent without user name and password.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        calendar_data.set_headers("", "", "Mozilla/5.0")

    def test_set_username_and_password(self, logger):
        """Test setting user name and password without user agent.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        calendar_data.set_headers("username", "password", "")

    def test_set_username_password_and_user_agent(self, logger):
        """Test setting user name and password without user agent.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        calendar_data.set_headers("username", "password", "Mozilla/5.0")

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

    def test_download_calendar_uses_self_opener(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        calendar_data._opener = opener  # pylint: disable=W0212
        calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar_handles_utf8BOM(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerUTF8BOM)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar_handles_utf16BOMBE(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerUTF16BOMBE)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar_handles_utf16BOMLE(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerUTF16BOMLE)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar_returns_none_for_really_bad_data(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerBadUTF)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

    def test_download_calendar_interprets_gzip(self, logger):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPGzipHandler)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    def test_download_calendar_bad_gzip(self, logger):
        """Test that None is cached for BadGzipFile.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPGzipHandlerBadGzip)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

    def test_download_calendar_bad_deflate(self, logger):
        """Test that None is cached for BadDeflate.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPGzipHandlerBadDeflate)
        install_opener(opener)
        calendar_data.download_calendar()
        assert calendar_data.get() is None

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
    def test_download_returns_new_data(self, mock_hanow, logger):
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
    def test_download_too_quickly_returns_old_data(self, mock_hanow, logger):
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
