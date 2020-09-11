"""Support for ICS Calendar."""
import aiohttp
import asyncio
import copy
import logging
from datetime import datetime, timedelta
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.request import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, HTTPDigestAuthHandler, build_opener, install_opener, urlopen

from icalevents import icalparser
import voluptuous as vol
from homeassistant.components.calendar import (ENTITY_ID_FORMAT,
                                               PLATFORM_SCHEMA,
                                               CalendarEventDevice,
                                               calculate_offset,
                                               is_offset_reached)
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_URL, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util import Throttle

VERSION = "2.0.0"

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = 'device_id'
CONF_CALENDARS = 'calendars'
CONF_CALENDAR = 'calendar'
CONF_INCLUDE_ALL_DAY = 'includeAllDay'

OFFSET = "!!"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    # pylint: disable=no-value-for-parameter
    vol.Optional(CONF_CALENDARS, default=[]):
        vol.All(cv.ensure_list, vol.Schema([
            vol.Schema({
                vol.Required(CONF_URL): vol.Url(),
                vol.Required(CONF_NAME): cv.string,
                vol.Optional(CONF_INCLUDE_ALL_DAY, default=False): cv.boolean,
                vol.Optional(CONF_USERNAME, default=''): cv.string,
                vol.Optional(CONF_PASSWORD, default=''): cv.string
            })
        ]))
})

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)


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
            CONF_PASSWORD: calendar.get(CONF_PASSWORD)
        }
        device_id = "{}".format(device_data[CONF_NAME])
        entity_id = generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        calendar_devices.append(
            ICSCalendarEventDevice(entity_id, device_data))

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

    @property
    def device_state_attributes(self):
        """Return the calendar entity's state attributes."""
        return {'offset_reached': self._offset_reached}

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
        return await self.data.async_get_events(hass, start_date, end_date)

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
        self.event = None

        if device_data[CONF_USERNAME] != '' \
           and device_data[CONF_PASSWORD] != '':
           passman = HTTPPasswordMgrWithDefaultRealm()
           passman.add_password(None, self.url, device_data[CONF_USERNAME], device_data[CONF_PASSWORD])
           basicAuthHandler = HTTPBasicAuthHandler(passman)
           digestAuthHandler = HTTPDigestAuthHandler(passman)
           opener = build_opener(digestAuthHandler, basicAuthHandler)
           install_opener(opener)


    def _downloadAndParseCalendar(self):
        try:
            calendar_data = urlopen(self.url).read().decode().replace('\0', '')
        except HTTPError as http_error:
            _LOGGER.error("%s: Failed to open url: %s",
                          self.name, http_error.reason)
        except ContentTooShortError as content_too_short_error:
            _LOGGER.error("%s: Could not download calendar data: %s",
                          self.name, content_too_short_error.reason)
        except URLError as url_error:
            _LOGGER.error("%s: Failed to open url: %s",
                          self.name, url_error.reason)
        # Any other errors are probably parse errors...
        except Error as error:
            _LOGGER.error("%s: Failed to parse iCalendar: %s",
                          self.name, error.reason)
        return calendar_data

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        event_list = []
        calendar_data = await hass.async_add_job(self._downloadAndParseCalendar)
        events = icalparser.parse_events(content=calendar_data, start=start_date, end=end_date)
        if events is not None:
            for event in events:
                if event.all_day and not self.include_all_day:
                    continue
                uid = None
                if hasattr(event, 'uid') and event.uid != -1:
                    uid = event.uid
                data = {
                    'uid': uid,
                    'summary': event.summary,
                    'start': self.get_date_formatted(event.start.astimezone(), event.all_day),
                    'end': self.get_date_formatted(event.end.astimezone(), event.all_day),
                    'location': event.location,
                    'description': event.description
                }
                # Note that we return a formatted date for start and end here,
                # but a different format for self.event!
                event_list.append(data)

        return event_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data."""
        now = datetime.now().astimezone()
        calendar_data = self._downloadAndParseCalendar()
        events = icalparser.parse_events(content=calendar_data, end=now)
        if events is not None:
            temp_event = None
            for event in events:
                if event.all_day and not self.include_all_day:
                    continue
                else:
                    event.start = event.start.astimezone()
                    event.end = event.end.astimezone()
                    # This first case probably isn't needed; when writing this
                    # code, I noticed that if an event hasn't started yet, it
                    # won't be returned at all.  I've left the condition in,
                    # just in case that changes in the future.
                    if event.start > now or event.end < now:
                        continue
                if temp_event is None:
                    temp_event = event
                elif temp_event.end > event.end:
                    temp_event = event

            if temp_event is None:
                self.event = None
                return True

            self.event = {
                'summary': temp_event.summary,
                'start': self.get_hass_date(temp_event.start, temp_event.all_day),
                'end': self.get_hass_date(temp_event.end, temp_event.all_day),
                'location': temp_event.location,
                'description': temp_event.description
            }
            return True

        return False

    @staticmethod
    def get_date_formatted(dt, is_all_day):
        """Return the formatted date"""
        # Note that all day events should have a time of 0, and the timezone
        # must be local.
        if is_all_day:
            return dt.strftime("%Y-%m-%d")

        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    @staticmethod
    def get_hass_date(dt, is_all_day):
        """Return the wrapped and formatted date"""
        if is_all_day:
            return {'date': ICSCalendarData.get_date_formatted(dt, is_all_day)}
        return {'dateTime': ICSCalendarData.get_date_formatted(dt, is_all_day)}
