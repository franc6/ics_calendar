"""Test the calendar class."""
import copy
import logging
from unittest.mock import ANY, Mock, patch

import pytest
from dateutil import parser as dtparser
from homeassistant.components.calendar import CalendarEvent
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.template import DATE_STR_FORMAT
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as hadt

from custom_components.ics_calendar.const import DOMAIN, UPGRADE_URL

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True, name="skip_notifications")
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch(
        "homeassistant.components.persistent_notification.async_create"
    ), patch("homeassistant.components.persistent_notification.async_dismiss"):
        yield


@pytest.fixture(autouse=True)
def ics_enable_custom_integrations(enable_custom_integrations):
    """Provide enable_custom_integrations fixture for HA."""
    yield


@pytest.fixture(autouse=True)
def prevent_io():
    """Fixture to prevent certain I/O from happening."""
    with patch("homeassistant.components.http.ban.load_yaml_config_file"):
        yield


@pytest.fixture(autouse=True)
def mock_http(hass):
    """Provide mock_http fixture to mock the HomeAssistant.http object."""
    hass.http = Mock()


@pytest.fixture(autouse=True)
def mock_http_start_stop():
    """Fixture to avoid stop/start of http server."""
    with patch(
        "homeassistant.components.http.start_http_server_and_save_config"
    ), patch("homeassistant.components.http.HomeAssistantHTTP.stop"):
        yield


def _mocked_event():
    """Provide fixture to mock a single event."""
    return CalendarEvent(
        summary="Test event",
        start=hadt.as_local(dtparser.parse("2022-01-03T00:00:00")),
        end=hadt.as_local(dtparser.parse("2022-01-03T05:00:00")),
        location="Test location",
        description="Test description",
    )


def _mocked_event_list():
    """Provide fixture to mock a list of events."""
    return [
        CalendarEvent(
            summary="Test event 2",
            start=dtparser.parse("2022-01-04T00:00:00Z"),
            end=dtparser.parse("2022-01-04T05:00:00Z"),
            location="Test location",
            description="Test description",
        ),
        CalendarEvent(
            summary="Test event",
            start=dtparser.parse("2022-01-03T00:00:00Z"),
            end=dtparser.parse("2022-01-03T05:00:00Z"),
            location="Test location",
            description="Test description",
        ),
        CalendarEvent(
            summary="Test event 3",
            start=dtparser.parse("2022-01-05T00:00:00Z"),
            end=dtparser.parse("2022-01-05T05:00:00Z"),
            location="Test location",
            description="Test description",
        ),
    ]


def _mocked_event_allday():
    """Provide fixture to mock a single all day event."""
    return CalendarEvent(
        summary="Test event",
        start=dtparser.parse("2022-01-03").date(),
        end=dtparser.parse("2022-01-04").date(),
        location="Test location",
        description="Test description",
    )


def _mocked_calendar_data(file_name):
    """Return contents of file_name."""
    with open(file_name, encoding="utf-8") as file_handle:
        data = file_handle.read()
    return data


class TestCalendar:
    """Test Calendar class."""

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup(
        self, mock_event, mock_get, mock_download, hass, noallday_config
    ):
        """Test basic setup of platform not including all day events."""
        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.noallday")
        assert state.name == "noallday"

        mock_event.assert_called_with(
            include_all_day=False, now=ANY, days=ANY, offset_hours=0
        )

    async def test_calendar_setup_no_config(self, hass, caplog):
        """Test basic setup of platform not including all day events."""
        with caplog.at_level(logging.ERROR):
            assert await async_setup_component(hass, DOMAIN, {})
            await hass.async_block_till_done()
        assert UPGRADE_URL in caplog.text

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData"
        ".set_headers",
        return_value=None,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_all_day(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_sh,
        hass,
        allday_config,
    ):
        """Test basic setup of platform with user name and password."""
        assert await async_setup_component(hass, DOMAIN, allday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.allday")
        assert state.name == "allday"

        mock_event.assert_called_with(
            include_all_day=True, now=ANY, days=ANY, offset_hours=0
        )

    @pytest.mark.parametrize("set_tz", ["utc"], indirect=True)
    @patch(
        "custom_components.ics_calendar.calendar.hanow",
        return_value=dtparser.parse("2021-01-03T00:00:01Z"),
    )
    @patch(
        "homeassistant.util.dt.now",
        return_value=dtparser.parse("2021-01-03T00:00:01Z"),
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_event_list",
        return_value=_mocked_event_list(),
    )
    async def test_calendar_setup_prefix(
        self,
        mock_event_list,
        mock_event,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        set_tz,
        hass,
        prefix_config,
        get_api_events,
    ):
        """Test basic setup of platform not including all day events."""
        mocked_event = copy.deepcopy(mock_event())

        assert await async_setup_component(hass, DOMAIN, prefix_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.prefix")
        assert state.name == "prefix"

        assert dict(state.attributes) == {
            "friendly_name": "prefix",
            "message": prefix_config[DOMAIN]["calendars"][0]["prefix"]
            + mocked_event.summary,
            "all_day": False,
            "start_time": mocked_event.start.strftime(DATE_STR_FORMAT),
            "end_time": mocked_event.end.strftime(DATE_STR_FORMAT),
            "location": mocked_event.location,
            "description": mocked_event.description,
            "offset_reached": False,
        }

        events = await get_api_events("calendar.prefix")
        assert len(events) == len(mock_event_list())
        for event in events:
            assert event["summary"].startswith(
                prefix_config[DOMAIN]["calendars"][0]["prefix"]
            )

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_negative_offset_hours(
        self,
        mock_event,
        mock_get,
        mock_download,
        hass,
        negative_offset_hours_config,
    ):
        """Test basic setup of platform not including all day events."""
        assert await async_setup_component(
            hass, DOMAIN, negative_offset_hours_config
        )
        await hass.async_block_till_done()

        state = hass.states.get("calendar.negative_offset_hours")
        assert state.name == "negative_offset_hours"

        mock_event.assert_called_with(
            include_all_day=False, now=ANY, days=ANY, offset_hours=-5
        )

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_positive_offset_hours(
        self,
        mock_event,
        mock_get,
        mock_download,
        hass,
        positive_offset_hours_config,
    ):
        """Test basic setup of platform not including all day events."""
        assert await async_setup_component(
            hass, DOMAIN, positive_offset_hours_config
        )
        await hass.async_block_till_done()

        state = hass.states.get("calendar.positive_offset_hours")
        assert state.name == "positive_offset_hours"

        mock_event.assert_called_with(
            include_all_day=False, now=ANY, days=ANY, offset_hours=5
        )

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData"
        ".set_headers",
        return_value=None,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_acceptheader(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_sh,
        hass,
        acceptheader_config,
    ):
        """Test basic setup of platform with user name and password."""
        assert await async_setup_component(hass, DOMAIN, acceptheader_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.acceptheader")
        assert state.name == "acceptheader"
        mock_sh.assert_called_with(
            "",
            "",
            "",
            acceptheader_config[DOMAIN]["calendars"][0]["accept_header"],
        )

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData"
        ".set_headers",
        return_value=None,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_useragent(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_sh,
        hass,
        useragent_config,
    ):
        """Test basic setup of platform with user name and password."""
        assert await async_setup_component(hass, DOMAIN, useragent_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.useragent")
        assert state.name == "useragent"
        mock_sh.assert_called_with(
            "",
            "",
            useragent_config[DOMAIN]["calendars"][0]["user_agent"],
            "",
        )

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData"
        ".set_headers",
        return_value=None,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_userpass(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_sh,
        hass,
        userpass_config,
    ):
        """Test basic setup of platform with user name and password."""
        assert await async_setup_component(hass, DOMAIN, userpass_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.userpass")
        assert state.name == "userpass"
        mock_sh.assert_called_with(
            userpass_config[DOMAIN]["calendars"][0]["username"],
            userpass_config[DOMAIN]["calendars"][0]["password"],
            "",
            "",
        )

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData"
        ".set_timeout",
        return_value=None,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_calendar_setup_timeout(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_st,
        hass,
        timeout_config,
    ):
        """Test basic setup of platform with connection_timeout."""
        assert await async_setup_component(hass, DOMAIN, timeout_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.timeout")
        assert state.name == "timeout"
        mock_st.assert_called_with(
            float(
                timeout_config[DOMAIN]["calendars"][0]["connection_timeout"]
            ),
        )

    @patch(
        "custom_components.ics_calendar.calendar.hanow",
        return_value=dtparser.parse("2021-01-03T00:00:01Z"),
    )
    @patch(
        "homeassistant.util.dt.now",
        return_value=dtparser.parse("2021-01-03T00:00:01Z"),
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=True,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".set_content",
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_event_list",
        return_value=_mocked_event_list(),
    )
    async def test_download_success(
        self,
        mock_event_list,
        mock_set_content,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        get_api_events,
        noallday_config,
    ):
        """Test get_api_events."""
        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.noallday")
        assert state.name == "noallday"
        mock_set_content.assert_called_with(
            _mocked_calendar_data("tests/allday.ics")
        )
        mock_set_content.reset_mock()

        events = await get_api_events("calendar.noallday")
        assert len(events) == len(mock_event_list())
        mock_set_content.assert_called_with(
            _mocked_calendar_data("tests/allday.ics")
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
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_future_event(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        set_tz,
        noallday_config,
    ):
        """Test state for a future event."""
        # Must reset return_value here or only the first parametrized run will
        # succeed.
        mock_event.return_value = copy.deepcopy(_mocked_event())
        # Make a deep copy into mocked_event now, so we can use it with
        # strftime later.
        mocked_event = copy.deepcopy(mock_event())

        mock_dt_now.return_value = hadt.as_local(
            dtparser.parse("2022-01-01T00:00:01")
        )
        mock_now.return_value = hadt.as_local(
            dtparser.parse("2022-01-01T00:00:01")
        )

        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.noallday")

        assert dict(state.attributes) == {
            "friendly_name": "noallday",
            "message": mocked_event.summary,
            "all_day": False,
            "start_time": mocked_event.start.strftime(DATE_STR_FORMAT),
            "end_time": mocked_event.end.strftime(DATE_STR_FORMAT),
            "location": mocked_event.location,
            "description": mocked_event.description,
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
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_ongoing_event(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        set_tz,
        noallday_config,
    ):
        """Test state for an on-going event."""
        # Must reset return_value here or only the first parametrized run will
        # succeed.
        mock_event.return_value = copy.deepcopy(_mocked_event())
        # Make a deep copy into mocked_event now, so we can use it with
        # strftime later.
        mocked_event = copy.deepcopy(mock_event())

        mock_dt_now.return_value = hadt.as_local(
            dtparser.parse("2022-01-03T00:00:01")
        )
        mock_now.return_value = hadt.as_local(
            dtparser.parse("2022-01-03T00:00:01")
        )

        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.noallday")

        assert dict(state.attributes) == {
            "friendly_name": "noallday",
            "message": mocked_event.summary,
            "all_day": False,
            "start_time": mocked_event.start.strftime(DATE_STR_FORMAT),
            "end_time": mocked_event.end.strftime(DATE_STR_FORMAT),
            "location": mocked_event.location,
            "description": mocked_event.description,
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
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event(),
    )
    async def test_ongoing_event_exception(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        noallday_config,
    ):
        """Test state if exception is thrown."""
        mock_event.side_effect = Exception("Parse Error")
        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.noallday")

        assert state.state == STATE_OFF
        assert dict(state.attributes) == {
            "friendly_name": "noallday",
            "offset_reached": False,
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
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_current_event",
        return_value=_mocked_event_allday(),
    )
    async def test_ongoing_event_allday(
        self,
        mock_event,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        set_tz,
        allday_config,
    ):
        """Test state if on-going event is all day."""
        # Must reset return_value here or only the first parametrized run will
        # succeed.
        mock_event.return_value = copy.deepcopy(_mocked_event_allday())
        # Make a deep copy into mocked_event now, so we can use it with
        # strftime later.
        mocked_event = copy.deepcopy(mock_event())

        mock_dt_now.return_value = hadt.as_local(
            dtparser.parse("2022-01-03T00:00:01")
        )
        mock_now.return_value = hadt.as_local(
            dtparser.parse("2022-01-03T00:00:01")
        )

        assert await async_setup_component(hass, DOMAIN, allday_config)
        await hass.async_block_till_done()

        state = hass.states.get("calendar.allday")

        assert dict(state.attributes) == {
            "friendly_name": "allday",
            "message": mocked_event.summary,
            "all_day": True,
            "start_time": mocked_event.start.strftime(DATE_STR_FORMAT),
            "end_time": mocked_event.end.strftime(DATE_STR_FORMAT),
            "location": mocked_event.location,
            "description": mocked_event.description,
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
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_event_list",
        return_value=_mocked_event_list(),
    )
    async def test_get_events(
        self,
        mock_event_list,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        get_api_events,
        noallday_config,
    ):
        """Test get_api_events."""
        assert await async_setup_component(hass, DOMAIN, noallday_config)
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
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_event_list",
        return_value=_mocked_event_list(),
    )
    async def test_get_events_exception(
        self,
        mock_event_list,
        mock_get,
        mock_download,
        mock_dt_now,
        mock_now,
        hass,
        get_api_events,
        noallday_config,
    ):
        """Test get_api_events when exception is thrown."""
        mock_event_list.side_effect = BaseException("Failed to get events")
        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        events = await get_api_events("calendar.noallday")
        assert len(events) == 0

    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.download_calendar",
        return_value=False,
    )
    @patch(
        "custom_components.ics_calendar.calendardata.CalendarData.get",
        return_value=_mocked_calendar_data("tests/allday.ics"),
    )
    @patch(
        "custom_components.ics_calendar.parsers.parser_rie.ParserRIE"
        ".get_event_list",
        return_value=_mocked_event_list(),
    )
    async def test_create_event_raises_error(
        self,
        mock_event_list,
        mock_get,
        mock_download,
        hass,
        noallday_config,
    ):
        """Test that create_event raises an error."""
        assert await async_setup_component(hass, DOMAIN, noallday_config)
        await hass.async_block_till_done()

        with pytest.raises(HomeAssistantError):
            await hass.services.async_call(
                "calendar",
                "create_event",
                {
                    "start_date_time": "2024-01-15T12:00:00+00:00",
                    "end_date_time": "2024-01-15T12:01:00+00:00",
                    "summary": "Test event",
                },
                target={"entity_id": "calendar.noallday"},
                blocking=True,
            )
