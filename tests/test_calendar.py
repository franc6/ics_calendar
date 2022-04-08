"""Test the calendar class."""
import asyncio
import copy
from http import HTTPStatus
from unittest.mock import Mock, patch

import aiotask_context
import pytest
from dateutil import parser as dtparser
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as hadt

from custom_components.ics_calendar.const import PLATFORM

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def enable_custom_integrations(enable_custom_integrations):
    """Provide enable_custom_integrations fixture for HA."""
    yield


@pytest.fixture(autouse=True)
def loop_factory():
    """Provide loop_factory fixture for HA."""
    return asyncio.new_event_loop


@pytest.fixture(autouse=True)
def mock_http(hass):
    """Provide mock_http fixture to mock the HomeAssistant.http object."""
    hass.http = Mock()


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


@pytest.fixture(autouse=True)
def set_task_factory(loop):
    """Provide set_task_factory fixture for HA."""
    loop.set_task_factory(aiotask_context.task_factory)


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


def _mocked_event():
    """Provide fixture to mock a single event."""
    return {
        "summary": "Test event",
        "start": dtparser.parse("2022-01-03T00:00:00"),
        "end": dtparser.parse("2022-01-03T05:00:00"),
        "location": "Test location",
        "description": "Test description",
        "all_day": False,
    }


def _mocked_event_list():
    """Provide fixture to mock a list of events."""
    return [
        {
            "summary": "Test event 2",
            "start": dtparser.parse("2022-01-04T00:00:00Z"),
            "end": dtparser.parse("2022-01-04T05:00:00Z"),
            "location": "Test location",
            "description": "Test description",
            "all_day": False,
        },
        {
            "summary": "Test event",
            "start": dtparser.parse("2022-01-03T00:00:00Z"),
            "end": dtparser.parse("2022-01-03T05:00:00Z"),
            "location": "Test location",
            "description": "Test description",
            "all_day": False,
        },
        {
            "summary": "Test event 3",
            "start": dtparser.parse("2022-01-05T00:00:00Z"),
            "end": dtparser.parse("2022-01-05T05:00:00Z"),
            "location": "Test location",
            "description": "Test description",
            "all_day": False,
        },
    ]


def _mocked_event_allday():
    """Provide fixture to mock a single all day event."""
    return {
        "summary": "Test event",
        "start": dtparser.parse("2022-01-03"),
        "end": dtparser.parse("2022-01-04"),
        "location": "Test location",
        "description": "Test description",
        "all_day": True,
    }


def _mocked_calendar_data(file_name):
    """Return contents of file_name."""
    with open(file_name) as file_handle:
        data = file_handle.read()
    return data


@pytest.fixture()
def allday_config():
    """Provide fixture for configuration that includes allday events."""
    return {
        "calendar": {
            "platform": PLATFORM,
            "calendars": [
                {
                    "name": "allday",
                    "url": "http://test.local/tests/allday.ics",
                    "includeAllDay": "true",
                    "days": "1",
                }
            ],
        }
    }


@pytest.fixture()
def noallday_config():
    """Provide fixture for configuration that does not include allday events."""
    return {
        "calendar": {
            "platform": PLATFORM,
            "calendars": [
                {
                    "name": "noallday",
                    "url": "http://test.local/tests/allday.ics",
                    "includeAllDay": "false",
                    "days": "1",
                }
            ],
        }
    }


@pytest.fixture()
def userpass_config():
    """Provide fixture for configuration that uses user name and password."""
    return {
        "calendar": {
            "platform": PLATFORM,
            "calendars": [
                {
                    "name": "userpass",
                    "url": "http://test.local/tests/allday.ics",
                    "includeAllDay": "false",
                    "days": "1",
                    "username": "username",
                    "password": "password",
                }
            ],
        }
    }


@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_current_event",
    return_value=_mocked_event(),
)
async def test_calendar_setup(mock_event, mock_get, hass, noallday_config):
    """Test basic setup of platform not including all day events."""
    assert await async_setup_component(hass, "calendar", noallday_config)
    await hass.async_block_till_done()

    state = hass.states.get("calendar.noallday")
    assert state.name == "noallday"


@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.set_user_name_password",
    return_value=None,
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_current_event",
    return_value=_mocked_event(),
)
async def test_calendar_setup_userpass(
    mock_event, mock_get, mock_sup, hass, userpass_config
):
    """Test basic setup of platform with user name and password."""
    assert await async_setup_component(hass, "calendar", userpass_config)
    await hass.async_block_till_done()

    state = hass.states.get("calendar.userpass")
    assert state.name == "userpass"
    mock_sup.assert_called_with(
        userpass_config["calendar"]["calendars"][0]["username"],
        userpass_config["calendar"]["calendars"][0]["password"],
    )


@pytest.mark.parametrize(
    "set_tz", ["utc", "chicago", "baghdad"], indirect=True
)
@patch(
    "custom_components.ics_calendar.calendar.hanow",
    return_value=dtparser.parse("2022-01-01T00:00:01"),
)
@patch(
    "homeassistant.util.dt.now",
    return_value=dtparser.parse("2022-01-01T00:00:01"),
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_current_event",
    return_value=_mocked_event(),
)
async def test_future_event(
    mock_event, mock_get, mock_dt_now, mock_now, hass, set_tz, noallday_config
):
    """Test state for a future event."""
    # Must reset return_value here or only the first parametrized run will succeed.
    mock_event.return_value = copy.deepcopy(_mocked_event_allday())
    # Make a deep copy into mocked_event now, so we can use it with strftime later.
    mocked_event = copy.deepcopy(mock_event())
    mocked_event["start"] = hadt.as_local(mocked_event["start"])
    mocked_event["end"] = hadt.as_local(mocked_event["end"])

    mock_dt_now.return_value = hadt.as_local(
        dtparser.parse("2022-01-01T00:00:01")
    )
    mock_now.return_value = hadt.as_local(
        dtparser.parse("2022-01-01T00:00:01")
    )

    assert await async_setup_component(hass, "calendar", noallday_config)
    await hass.async_block_till_done()

    state = hass.states.get("calendar.noallday")

    assert dict(state.attributes) == {
        "message": mocked_event["summary"],
        "start_time": mocked_event["start"].strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": mocked_event["end"].strftime("%Y-%m-%d %H:%M:%S"),
        "all_day": mocked_event["all_day"],
        "friendly_name": "noallday",
        "location": mocked_event["location"],
        "description": mocked_event["description"],
        "offset_reached": False,
    }
    assert state.state == STATE_OFF


@pytest.mark.parametrize(
    "set_tz", ["utc", "chicago", "baghdad"], indirect=True
)
@patch(
    "custom_components.ics_calendar.calendar.hanow",
    return_value=dtparser.parse("2022-01-03T00:00:01"),
)
@patch(
    "homeassistant.util.dt.now",
    return_value=dtparser.parse("2022-01-03T00:00:01"),
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_current_event",
    return_value=_mocked_event(),
)
async def test_ongoing_event(
    mock_event, mock_get, mock_dt_now, mock_now, hass, set_tz, noallday_config
):
    """Test state for an on-going event."""
    # Must reset return_value here or only the first parametrized run will succeed.
    mock_event.return_value = copy.deepcopy(_mocked_event_allday())
    # Make a deep copy into mocked_event now, so we can use it with strftime later.
    mocked_event = copy.deepcopy(mock_event())
    mocked_event["start"] = hadt.as_local(mocked_event["start"])
    mocked_event["end"] = hadt.as_local(mocked_event["end"])

    mock_dt_now.return_value = hadt.as_local(
        dtparser.parse("2022-01-03T00:00:01")
    )
    mock_now.return_value = hadt.as_local(
        dtparser.parse("2022-01-03T00:00:01")
    )

    assert await async_setup_component(hass, "calendar", noallday_config)
    await hass.async_block_till_done()

    state = hass.states.get("calendar.noallday")

    assert dict(state.attributes) == {
        "message": mocked_event["summary"],
        "start_time": mocked_event["start"].strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": mocked_event["end"].strftime("%Y-%m-%d %H:%M:%S"),
        "all_day": mocked_event["all_day"],
        "friendly_name": "noallday",
        "location": mocked_event["location"],
        "description": mocked_event["description"],
        "offset_reached": False,
    }
    assert state.state == STATE_ON


@patch(
    "custom_components.ics_calendar.calendar.hanow",
    return_value=dtparser.parse("2022-01-03T00:00:01"),
)
@patch(
    "homeassistant.util.dt.now",
    return_value=dtparser.parse("2022-01-03T00:00:01"),
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_current_event",
    return_value=_mocked_event(),
)
async def test_ongoing_event_exception(
    mock_event, mock_get, mock_dt_now, mock_now, hass, noallday_config
):
    """Test state if exception is thrown."""
    mock_event.side_effect = Exception("Parse Error")
    assert await async_setup_component(hass, "calendar", noallday_config)
    await hass.async_block_till_done()

    state = hass.states.get("calendar.noallday")

    assert state.state == STATE_OFF
    assert dict(state.attributes) == {
        "friendly_name": "noallday",
    }


@pytest.mark.parametrize(
    "set_tz", ["utc", "chicago", "baghdad"], indirect=True
)
@patch(
    "custom_components.ics_calendar.calendar.hanow",
    return_value=dtparser.parse("2022-01-03T00:00:01"),
)
@patch(
    "homeassistant.util.dt.now",
    return_value=dtparser.parse("2022-01-03T00:00:01"),
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_current_event",
    return_value=_mocked_event_allday(),
)
async def test_ongoing_event_allday(
    mock_event, mock_get, mock_dt_now, mock_now, hass, set_tz, allday_config
):
    """Test state if on-going event is all day."""
    # Must reset return_value here or only the first parametrized run will succeed.
    mock_event.return_value = copy.deepcopy(_mocked_event_allday())
    # Make a deep copy into mocked_event now, so we can use it with strftime later.
    mocked_event = copy.deepcopy(mock_event())
    mocked_event["start"] = hadt.as_local(mocked_event["start"])
    mocked_event["end"] = hadt.as_local(mocked_event["end"])

    mock_dt_now.return_value = hadt.as_local(
        dtparser.parse("2022-01-03T00:00:01")
    )
    mock_now.return_value = hadt.as_local(
        dtparser.parse("2022-01-03T00:00:01")
    )

    assert await async_setup_component(hass, "calendar", allday_config)
    await hass.async_block_till_done()

    state = hass.states.get("calendar.allday")

    assert dict(state.attributes) == {
        "message": mocked_event["summary"],
        "start_time": mocked_event["start"].strftime("%Y-%m-%d 00:00:00"),
        "end_time": mocked_event["end"].strftime("%Y-%m-%d 00:00:00"),
        "all_day": mocked_event["all_day"],
        "friendly_name": "allday",
        "location": mocked_event["location"],
        "description": mocked_event["description"],
        "offset_reached": False,
    }
    assert state.state == STATE_ON


@patch(
    "custom_components.ics_calendar.calendar.hanow",
    return_value=dtparser.parse("2022-01-03T00:00:01Z"),
)
@patch(
    "homeassistant.util.dt.now",
    return_value=dtparser.parse("2022-01-03T00:00:01Z"),
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_event_list",
    return_value=_mocked_event_list(),
)
async def test_get_events(
    mock_event_list,
    mock_get,
    mock_dt_now,
    mock_now,
    hass,
    get_api_events,
    noallday_config,
):
    """Test get_api_events."""
    assert await async_setup_component(hass, "calendar", noallday_config)
    await hass.async_block_till_done()

    events = await get_api_events("calendar.noallday")
    assert len(events) == len(mock_event_list())


@patch(
    "custom_components.ics_calendar.calendar.hanow",
    return_value=dtparser.parse("2022-01-03T00:00:01Z"),
)
@patch(
    "homeassistant.util.dt.now",
    return_value=dtparser.parse("2022-01-03T00:00:01Z"),
)
@patch(
    "custom_components.ics_calendar.calendardata.CalendarData.get",
    return_value=_mocked_calendar_data("tests/allday.ics"),
)
@patch(
    "custom_components.ics_calendar.parsers.parser_rie.ParserRIE.get_event_list",
    return_value=_mocked_event_list(),
)
async def test_get_events_exception(
    mock_event_list,
    mock_get,
    mock_dt_now,
    mock_now,
    hass,
    get_api_events,
    noallday_config,
):
    """Test get_api_events when exception is thrown."""
    mock_event_list.side_effect = BaseException("Failed to get events")
    assert await async_setup_component(hass, "calendar", noallday_config)
    await hass.async_block_till_done()

    events = await get_api_events("calendar.noallday")
    assert len(events) == 0
