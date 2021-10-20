"""Support for ICS Calendar."""
import copy
import logging
from datetime import datetime, timedelta
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.request import (
    HTTPPasswordMgrWithDefaultRealm,
    HTTPBasicAuthHandler,
    HTTPDigestAuthHandler,
    build_opener,
    install_opener,
    urlopen,
)

import voluptuous as vol
from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    CalendarEventDevice,
    calculate_offset,
    is_offset_reached,
)
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_URL, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util import Throttle
from .icalendarparser import ICalendarParser

VERSION = "2.0.0"

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = "device_id"
CONF_CALENDARS = "calendars"
CONF_CALENDAR = "calendar"
CONF_INCLUDE_ALL_DAY = "includeAllDay"
CONF_PARSER = "parser"

OFFSET = "!!"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        # pylint: disable=no-value-for-parameter
        vol.Optional(CONF_CALENDARS, default=[]): vol.All(
            cv.ensure_list,
            vol.Schema(
                [
                    vol.Schema(
                        {
                            vol.Required(CONF_URL): vol.Url(),
                            vol.Required(CONF_NAME): cv.string,
                            vol.Optional(
                                CONF_INCLUDE_ALL_DAY, default=False
                            ): cv.boolean,
                            vol.Optional(CONF_USERNAME, default=""): cv.string,
                            vol.Optional(CONF_PASSWORD, default=""): cv.string,
                            vol.Optional(CONF_PARSER, default="icalevents"): cv.string,
                        }
                    )
                ]
            ),
        )
    }
)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
# MIN_TIME_BETWEEN_DOWNLOADS is smaller than MIN_TIME_BETWEEN_UPDATES so that
# it won't be skipped if an explicit update is called.  Eventually, if these are
# configurable, we'll let end users worry about if they mean to have it happen
# that way.
MIN_TIME_BETWEEN_DOWNLOADS = timedelta(minutes=10)


def setup_platform(hass, config, add_entities, _=None):
    """Set up the ICS Calendar platform """
    _LOGGER.debug("Setting up ics calendars")
    calendar_devices = []
    for calendar in config.get(CONF_CALENDARS):
        device_data = {
            CONF_NAME: calendar.get(CONF_NAME),
            CONF_URL: calendar.get(CONF_URL),
            CONF_INCLUDE_ALL_DAY: calendar.get(CONF_INCLUDE_ALL_DAY),
            CONF_USERNAME: calendar.get(CONF_USERNAME),
            CONF_PASSWORD: calendar.get(CONF_PASSWORD),
            CONF_PARSER: calendar.get(CONF_PARSER),
        }
        device_id = "{}".format(device_data[CONF_NAME])
        entity_id = generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        calendar_devices.append(ICSCalendarEventDevice(entity_id, device_data))

    add_entities(calendar_devices)


class ICSCalendarEventDevice(CalendarEventDevice):
    """A device for getting the next Task from an ICS Calendar"""

    def __init__(self, entity_id, device_data):
        _LOGGER.debug("Initializing calendar: %s", device_data[CONF_NAME])
        self.data = ICSCalendarData(device_data)
        self.entity_id = entity_id
        self._event = None
        self._name = device_data[CONF_NAME]
        self._offset_reached = False
        self._last_call = None
        self._last_event_list = None

    @property
    def device_state_attributes(self):
        """Return the calendar entity's state attributes."""
        return {"offset_reached": self._offset_reached}

    @property
    def event(self):
        """Returns the current event for the calendar entity or None"""
        return self._event

    @property
    def name(self):
        """Returns the name of the calendar entity"""
        return self._name

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        if (
            self._last_event_list is None
            or self._last_call is None
            or (datetime.now() - self._last_call) > MIN_TIME_BETWEEN_UPDATES
        ):
            self._last_call = datetime.now()
            self._last_event_list = await self.data.async_get_events(
                hass, start_date, end_date
            )
        return self._last_event_list

    def update(self):
        """Update event data."""
        self.data.update()
        event = copy.deepcopy(self.data.event)
        if event is None:
            self._event = event
            return
        event = calculate_offset(event, OFFSET)
        self._offset_reached = is_offset_reached(event)
        self._event = event


class ICSCalendarData:
    """Calss to use the calendar ICS client object to get next event."""

    def __init__(self, device_data):
        """Set up how we are going to connect to the ICS Calendar"""
        self.name = device_data[CONF_NAME]
        self.url = device_data[CONF_URL]
        self.include_all_day = device_data[CONF_INCLUDE_ALL_DAY]
        self.parser = ICalendarParser.get_instance(device_data[CONF_PARSER])
        self.event = None
        self._calendar_data = None
        self._last_download = None

        if device_data[CONF_USERNAME] != "" and device_data[CONF_PASSWORD] != "":
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(
                None, self.url, device_data[CONF_USERNAME], device_data[CONF_PASSWORD]
            )
            basic_auth_handler = HTTPBasicAuthHandler(passman)
            digest_auth_handler = HTTPDigestAuthHandler(passman)
            opener = build_opener(digest_auth_handler, basic_auth_handler)
            install_opener(opener)

    def _download_calendar(self):
        if (
            self._calendar_data is None
            or self._last_download is None
            or (datetime.now() - self._last_download) > MIN_TIME_BETWEEN_DOWNLOADS
        ):
            self._last_download = datetime.now()
            self._calendar_data = None
            try:
                with urlopen(self.url) as conn:
                    self._calendar_data = conn.read().decode().replace("\0", "")
            except HTTPError as http_error:
                _LOGGER.error(f"{self.name}: Failed to open url: {http_error.reason}")
            except ContentTooShortError as content_too_short_error:
                _LOGGER.error(
                    f"{self.name}: Could not download calendar data: {content_too_short_error.reason}"
                )
            except URLError as url_error:
                _LOGGER.error(f"{self.name}: Failed to open url: {url_error.reason}")
            except:
                _LOGGER.error(f"{self.name}: Failed to open url!")
        return

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        event_list = []
        await hass.async_add_job(self._download_calendar)
        try:
            event_list = self.parser.get_event_list(
                content=self._calendar_data,
                start=start_date,
                end=end_date,
                include_all_day=self.include_all_day,
            )
        except:
            _LOGGER.error(f"{self.name}: Failed to parse ICS!")
            event_list = []

        return event_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data."""
        self._download_calendar()
        try:
            self.event = self.parser.get_current_event(
                content=self._calendar_data, include_all_day=self.include_all_day
            )
            return True
        except:
            _LOGGER.error(f"{self.name}: Failed to parse ICS!")

        return False
