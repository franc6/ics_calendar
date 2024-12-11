"""Test the CalendarData class."""

import email
import re
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch
from urllib.request import HTTPHandler
from urllib.response import addinfourl

import httpx
import pytest
from dateutil import parser as dtparser
from pytest_httpx import httpx_mock

from custom_components.ics_calendar.calendardata import CalendarData

BINARY_CALENDAR_DATA = b"calendar data"
BINARY_CALENDAR_DATA_2 = b"2 calendar data"
CALENDAR_DATA = "calendar data"
CALENDAR_DATA_2 = "2 calendar data"
CALENDAR_NAME = "TESTcalendar"

TEST_URL = "http://127.0.0.1/test/allday.ics"
TEST_TEMPLATE_URL = "http://127.0.0.1/test/{year}/{month}/allday.ics"
TEST_TEMPLATE_URL_REPLACED = "http://127.0.0.1/test/2022/01/allday.ics"


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


class MockHTTPHandlerTimeoutValue:
    """Mock HTTPHandler that reports timeout value."""

    def http_open(self, req):
        """Provide http_open to return the timeout value."""
        timeout_str = f"{req.timeout}"
        return mock_response(req, timeout_str.encode("utf-8"))


class TestCalendarData:
    """Test the CalendarData class."""

    def test_set_headers_none(self, logger, hass):
        """Test set_headers without user name, password, or user agent."""
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers("", "", "", "")

    def test_set_accept_header(self, logger, hass):
        """Test setting accept header by itself.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers("", "", "", "text/calendar")

    def test_set_user_agent(self, logger, hass):
        """Test setting user agent by itself.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers("", "", "Mozilla/5.0", "")

    def test_set_username_and_password(self, logger, hass):
        """Test setting user name and password by themselves.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers("username", "password", "", "")

    def test_set_username_password_and_user_agent(self, logger, hass):
        """Test setting user name and password with user agent.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers("username", "password", "Mozilla/5.0", "")

    def test_set_username_password_and_accept_header(self, logger, hass):
        """Test setting user name and password with accept header.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers("username", "password", "", "text/calendar")

    def test_set_all_headers(self, logger, hass):
        """Test setting all headers.

        This doesn't do much, since set_headers has no failure conditions.  We
        could test that it actually does what it's supposed to do, except that
        means checking the implementation.
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        calendar_data.set_headers(
            "username", "password", "Mozilla/5.0", "text/calendar"
        )

    def test_get(self, logger, hass):
        """Test get method retrieves cached data."""
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        set_calendar_data(calendar_data, CALENDAR_DATA)
        assert calendar_data.get() == CALENDAR_DATA

    @pytest.mark.asyncio
    async def test_download_calendar(self, logger, httpx_mock, hass):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_response(url=TEST_URL, content=BINARY_CALENDAR_DATA)
        await calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    @pytest.mark.asyncio
    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    async def test_download_calendar_interprets_templates(
        self, mock_hanow, logger, httpx_mock, hass
    ):
        """Test download_calendar sets cache from the mocked HTTPHandler.

        This test relies on the success of test_get!
        """
        httpx_mock.add_response(
            is_optional=True,
            url=TEST_TEMPLATE_URL_REPLACED,
            content=BINARY_CALENDAR_DATA,
        )
        httpx_mock.add_exception(
            BaseException("URL contains {year} template!"),
            is_optional=True,
            url=re.compile(".*[{]year[}]"),
        )
        httpx_mock.add_exception(
            BaseException("URL contains {month} template!"),
            is_optional=True,
            url=re.compile(".*[{]month[}]"),
        )
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_TEMPLATE_URL,
            timedelta(minutes=5),
        )
        await calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    @pytest.mark.asyncio
    async def test_download_calendar_decode_error(
        self, logger, httpx_mock, hass
    ):
        """Test that None is cached for a decode error.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_exception(httpx.DecodingError("Decoding error"))
        await calendar_data.download_calendar()
        assert calendar_data.get() is None

    @pytest.mark.asyncio
    async def test_download_calendar_HTTPError(self, logger, httpx_mock, hass):
        """Test that None is cached for HTTPError.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_exception(httpx.HTTPError("Generic error"))
        await calendar_data.download_calendar()

    @pytest.mark.asyncio
    async def test_download_calendar_InvalidURL(
        self, logger, httpx_mock, hass
    ):
        """Test that None is cached for InvalidURL.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_exception(httpx.InvalidURL("Invalid URL"))
        await calendar_data.download_calendar()
        assert calendar_data.get() is None

    @pytest.mark.asyncio
    async def test_download_calendar_TimeoutException(
        self, logger, httpx_mock, hass
    ):
        """Test that None is cached for TimeoutException.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        timeout = 1.5
        calendar_data.set_timeout(timeout)
        httpx_mock.add_exception(
            httpx.TimeoutException("timeout"),
            match_extensions={
                "timeout": {
                    "connect": timeout,
                    "read": timeout,
                    "write": timeout,
                    "pool": timeout,
                }
            },
        )
        await calendar_data.download_calendar()
        assert calendar_data.get() is None

    @pytest.mark.asyncio
    async def test_download_calendar_HTTPStatusError(
        self, logger, httpx_mock, hass
    ):
        """Test that None is cached for HTTPStatusError.

        This test relies on the success of test_get!
        """
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_response(status_code=500)
        await calendar_data.download_calendar()
        assert calendar_data.get() is None

    @pytest.mark.asyncio
    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    async def test_download_returns_new_data(
        self, mock_hanow, logger, httpx_mock, hass
    ):
        """Test that get causes downloads if enough time has passed."""
        mock_hanow.side_effect = [
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:05:05"),
            dtparser.parse("2022-01-01T00:05:05"),
            dtparser.parse("2022-01-01T00:05:05"),
        ]
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_response(content=BINARY_CALENDAR_DATA)
        httpx_mock.add_response(content=BINARY_CALENDAR_DATA_2)
        assert await calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

        assert await calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA_2

    @pytest.mark.asyncio
    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    async def test_download_too_quickly_returns_old_data(
        self, mock_hanow, logger, httpx_mock, hass
    ):
        """Test that get does not download if not enough time has passed."""
        mock_hanow.side_effect = [
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:04:59"),
            dtparser.parse("2022-01-01T00:04:59"),
        ]
        calendar_data = CalendarData(
            httpx.AsyncClient(),
            logger,
            CALENDAR_NAME,
            TEST_URL,
            timedelta(minutes=5),
        )
        httpx_mock.add_response(
            url=TEST_URL, content=BINARY_CALENDAR_DATA, is_optional=True
        )
        httpx_mock.add_response(
            url=TEST_URL, content=BINARY_CALENDAR_DATA_2, is_optional=True
        )
        assert await calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

        assert not await calendar_data.download_calendar()
        assert calendar_data.get() == CALENDAR_DATA

    # This isn't a good way to test this, since it relies on knowing how
    # HTTPHandler passes the timeout, but since we're mocking that anyway,
    # we might as well do it here, and use our knowledge. :(
    # def test_download_calendar_has_timeout(self, logger, hass):
    #    """Test that timeout is set properly."""
    #    timeout = 1.5
    #    timeout_str = f"{timeout}"
    #    calendar_data = CalendarData(
    #        httpx.AsyncClient(),
    #        logger,
    #        CALENDAR_NAME,
    #        TEST_URL,
    #        timedelta(minutes=5)
    #    )
    #    calendar_data.set_timeout(timeout)
    #    opener = build_opener(MockHTTPHandlerTimeoutValue)
    #    install_opener(opener)
    #    assert await calendar_data.download_calendar()
    #    assert calendar_data.get() == timeout_str
