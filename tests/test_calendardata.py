import pytest
from datetime import timedelta
from dateutil import parser as dtparser
import logging
from unittest.mock import MagicMock, Mock, patch
from custom_components.ics_calendar.calendardata import CalendarData
from io import BytesIO
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.request import build_opener, install_opener, HTTPHandler
from urllib.response import addinfourl

BINARY_CALENDAR_DATA = b"calendar data"
BINARY_CALENDAR_DATA_2 = b"2 calendar data"
CALENDAR_DATA = "calendar data"
CALENDAR_DATA_2 = "2 calendar data"
CALENDAR_NAME = "TESTcalendar"
TEST_URL = "http://127.0.0.1/test/allday.ics"


@pytest.fixture(autouse=True)
def logger():
    return logging.getLogger(__name__)


def setCalendarData(cd, data):
    cd._calendar_data = data


def mock_response(req, data):
    resp = addinfourl(BytesIO(data), "message", req.get_full_url())
    resp.code = 200
    resp.msg = "OK"
    return resp


class MockHTTPHandlerContentTooShortError(HTTPHandler):
    def http_open(self, req):
        raise ContentTooShortError("Expected 1000 bytes", CALENDAR_DATA)


class MockHTTPHandlerHTTPError(HTTPHandler):
    def http_open(self, req):
        raise HTTPError(404, "not found", None, None, None)


class MockHTTPHandlerURLError(HTTPHandler):
    def http_open(self, req):
        raise URLError("bad url")


class MockHTTPHandlerError(HTTPHandler):
    def http_open(self, req):
        raise Error("Unknown error")


class MockHTTPHandler(HTTPHandler):
    def http_open(self, req):
        return mock_response(req, BINARY_CALENDAR_DATA)


class MockHTTPHandler2(HTTPHandler):
    def http_open(self, req):
        return mock_response(req, BINARY_CALENDAR_DATA_2)


class TestCalendarData:
    def test_set_username_and_password(self):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        calendarData.setUserNameAndPassword("username", "password")

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData._download_calendar"
    )
    def test_get(self, mock_download):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        mock_download.side_effect = setCalendarData(calendarData, CALENDAR_DATA)
        assert calendarData.get() == CALENDAR_DATA

    def test_download_calendar(self, logger):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        install_opener(opener)
        calendarData._download_calendar()
        assert calendarData.get() == CALENDAR_DATA

    def test_download_calendar_ContentTooShortError(self, logger):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerContentTooShortError)
        install_opener(opener)
        calendarData._download_calendar()
        assert calendarData.get() == None

    def test_download_calendar_HTTPError(self, logger):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerHTTPError)
        install_opener(opener)
        calendarData._download_calendar()
        assert calendarData.get() == None

    def test_download_calendar_URLError(self, logger):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerURLError)
        install_opener(opener)
        calendarData._download_calendar()
        assert calendarData.get() == None

    def test_download_calendar_Error(self, logger):
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandlerError)
        install_opener(opener)
        calendarData._download_calendar()
        assert calendarData.get() == None

    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    def test_get_returns_new_data(self, mock_hanow, logger):
        mock_hanow.side_effect = [
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:05:05"),
        ]
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        install_opener(opener)
        assert calendarData.get() == CALENDAR_DATA

        opener = build_opener(MockHTTPHandler2)
        install_opener(opener)
        assert calendarData.get() == CALENDAR_DATA_2


    @patch(
        "custom_components.ics_calendar.calendardata.hanow",
        return_value=dtparser.parse("2022-01-01T00:00:00"),
    )
    def test_get_too_quickly_returns_old_data(self, mock_hanow, logger):
        mock_hanow.side_effect = [
            dtparser.parse("2022-01-01T00:00:00"),
            dtparser.parse("2022-01-01T00:04:59"),
        ]
        calendarData = CalendarData(
            logger, CALENDAR_NAME, TEST_URL, timedelta(minutes=5)
        )
        opener = build_opener(MockHTTPHandler)
        install_opener(opener)
        assert calendarData.get() == CALENDAR_DATA

        opener = build_opener(MockHTTPHandler2)
        install_opener(opener)
        assert calendarData.get() == CALENDAR_DATA
