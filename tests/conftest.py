"""Fixtures and helpers for tests."""
import json
import logging
import time
from http import HTTPStatus

import pytest
from dateutil import parser as dtparser

from custom_components.ics_calendar.const import DOMAIN
from custom_components.ics_calendar.icalendarparser import ICalendarParser


# Fixtures for test_calendar.py
@pytest.fixture
def set_tz(request):
    """Fake the timezone fixture."""
    return request.getfixturevalue(request.param)


@pytest.fixture
def utc(hass):
    """Set current time zone for HomeAssistant to UTC."""
    hass.config.set_time_zone("UTC")


@pytest.fixture
def chicago(hass):
    """Set current time zone for HomeAssistant to America/Chicago."""
    hass.config.set_time_zone("America/Chicago")


@pytest.fixture
def baghdad(hass):
    """Set current time zone for HomeAssistant to Asia/Baghdad."""
    hass.config.set_time_zone("Asia/Baghdad")


@pytest.fixture
def get_api_events(hass_client):
    """Provide fixture to mock get_api_events."""

    async def api_call(entity_id):
        client = await hass_client()
        response = await client.get(
            f"/api/calendars/{entity_id}?start=2022-01-01&end=2022-01-06"
        )
        assert response.status == HTTPStatus.OK
        return await response.json()

    return api_call


@pytest.fixture()
def allday_config():
    """Provide fixture for config that includes allday events."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "allday",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "true",
                    "days": "1",
                }
            ],
        }
    }


@pytest.fixture()
def noallday_config():
    """Provide fixture for config that does not include allday events."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "noallday",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                }
            ],
        }
    }


@pytest.fixture()
def positive_offset_hours_config():
    """Provide fixture for config that does not include allday events."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "positive_offset_hours",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "offset_hours": 5,
                }
            ],
        }
    }


@pytest.fixture()
def negative_offset_hours_config():
    """Provide fixture for config that does not include allday events."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "negative_offset_hours",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "offset_hours": -5,
                }
            ],
        }
    }


@pytest.fixture()
def prefix_config():
    """Provide fixture for config that does not include allday events."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "prefix",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "prefix": "PREFIX ",
                }
            ],
        }
    }


@pytest.fixture()
def acceptheader_config():
    """Provide fixture for config that uses user name and password."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "acceptheader",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "accept_header": "text/calendar",
                }
            ],
        }
    }


@pytest.fixture()
def useragent_config():
    """Provide fixture for config that uses user name and password."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "useragent",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "user_agent": "Mozilla/5.0",
                }
            ],
        }
    }


@pytest.fixture()
def userpass_config():
    """Provide fixture for config that uses user name and password."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "userpass",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "username": "username",
                    "password": "password",
                }
            ],
        }
    }


@pytest.fixture()
def timeout_config():
    """Provide fixture for config that uses user name and password."""
    return {
        DOMAIN: {
            "calendars": [
                {
                    "name": "timeout",
                    "url": "http://test.local/tests/allday.ics",
                    "include_all_day": "false",
                    "days": "1",
                    "connection_timeout": "1.5",
                }
            ],
        }
    }


# Fixtures and methods for test_parsers.py
def datetime_hook(pairs):
    """Parse datetime values from JSON."""
    _dict = {}
    for key, value in pairs:
        if isinstance(value, str):
            try:
                _dict[key] = dtparser.parse(value)
                if "T" not in value:
                    _dict[key] = _dict[key].date()
            except ValueError:
                _dict[key] = value
        else:
            _dict[key] = value
    return _dict


@pytest.fixture
def rie_parser():
    """Fixture for rie parser."""
    return ICalendarParser.get_instance("rie")


@pytest.fixture
def ics_parser():
    """Fixture for ics parser."""
    return ICalendarParser.get_instance("ics")


@pytest.fixture
def parser(which_parser, request):
    """Fixture for getting a parser.

    :param which_parser identifies the parser fixture, ParserRIE or ParserICS
    :type which_parser str
    :param request the request for the fixture
    :returns an instance of the requested parser
    :rtype ICalendarParser
    """
    return request.getfixturevalue(which_parser)


@pytest.fixture()
def calendar_data(file_name):
    """Return contents of a file with embedded NULL removed.

    :param fileName The name of the file
    :type str
    :returns the data
    :rtype str
    """
    with open(f"tests/{file_name}", encoding="utf-8") as file_handle:
        return file_handle.read().replace("\0", "")


@pytest.fixture()
def expected_name(file_name):
    """Return {fileName}.

    :param fileName: The base name of the file
    :type fileName: str
    """
    return file_name


@pytest.fixture()
def expected_data(file_name, expected_name):
    """Return content of tests/{fileName}.expected.json.

    :param fileName: The base name of the file
    :type fileName: str
    """
    with open(
        f"tests/{expected_name}.expected.json", encoding="utf-8"
    ) as file_handle:
        return json.loads(file_handle.read(), object_pairs_hook=datetime_hook)


@pytest.fixture(autouse=True)
def logger():
    """Provide autouse fixture for logger."""
    return logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def sleepless(monkeypatch):
    """Disable time.sleep() calls."""

    def sleep(seconds):
        pass

    monkeypatch.setattr(
        time,
        "sleep",
        sleep,
    )


@pytest.helpers.register
def assert_event_list_size(expected, event_list):
    """Assert event_list is not None and has the expected number of events.

    :param expected: The number of events that should be in event_list
    :type expected: int
    :param event_list: The array of events to check
    :type event_list: array
    """
    assert event_list is not None
    assert expected == len(event_list)


@pytest.helpers.register
def compare_event_list(expected, actual):
    """Assert that each item in expected matches the item in actual.

    :param expected: The data to expect
    :type expected: dict
    :param actual: The data to check
    :type actual: dict
    """
    for expected_part, actual_part in zip(expected, actual):
        pytest.helpers.compare_event(expected_part, actual_part)


@pytest.helpers.register
def compare_event(expected, actual):
    """Assert actual event matches expected event.

    :param expected: The event to expect
    :type expected: dict
    :param actual: The event to check
    :type actual: dict
    """
    for key in expected.keys():
        assert expected is not None
        assert actual is not None
        assert expected[key] == getattr(actual, key)
