"""Support for ICS Calendar."""
import copy
from datetime import datetime, timedelta
import logging
import re

VERSION="1.0.0"

import voluptuous as vol

from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    CalendarEventDevice,
    calculate_offset,
    get_date,
    is_offset_reached
)
from homeassistant.const import ( CONF_NAME, CONF_URL )
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util import Throttle, dt

from urllib.request import urlopen
import arrow
from ics import Calendar

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = 'device_id'
CONF_CALENDARS = 'calendars'
CONF_CALENDAR = 'calendar'
CONF_INCLUDE_ALL_DAY = 'includeAllDay'

OFFSET = "!!"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    # pylint: disable-no-value-for-parameter
    vol.Optional(CONF_CALENDARS, default=[]):
        vol.All(cv.ensure_list, vol.Schema([
            vol.Schema({
                vol.Required(CONF_URL): vol.Url(),
                vol.Required(CONF_NAME): cv.string,
                vol.Optional(CONF_INCLUDE_ALL_DAY, default=False): cv.boolean
            })
        ]))
})

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

def setup_platform(hass, config, add_entities, disc_info=None):
    """Set u p the ICS Calendar platform ."""
    _LOGGER.debug("Setting up ics calendars")
    calendar_devices = []
    for calendar in config.get(CONF_CALENDARS):
        device_data  = {
                CONF_NAME: calendar.get(CONF_NAME),
                CONF_URL: calendar.get(CONF_URL),
                CONF_INCLUDE_ALL_DAY: calendar.get(CONF_INCLUDE_ALL_DAY),
        }
        device_id = "{}".format(device_data[CONF_NAME])
        entity_id = generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        calendar_devices.append(
                ICSCalendarEventDevice(entity_id, device_data))

    add_entities(calendar_devices)

class ICSCalendarEventDevice(CalendarEventDevice):
    """A device for getting the next Task from an ICS Calendar."""

    def __init__(self, entity_id, device_data):
        _LOGGER.debug("Initializing calendar: '%s'", device_data[CONF_NAME])
        self.data = ICSCalendarData(device_data)
        self.entity_id = entity_id
        self._event = None
        self._name = device_data[CONF_NAME]
        self._offset_reached = False

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {"offset_reached": self._offset_reached}

    @property
    def event(self):
        return self._event

    @property
    def name(self):
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

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        c = Calendar(urlopen(self.url).read().decode())
        ar_start = arrow.get(start_date)
        ar_end = arrow.get(end_date)

        event_list = []
        for event in c.timeline.included(ar_start, ar_end):
            if event.all_day and not self.include_all_day:
                continue
            uid = None
            if hasattr(event, 'uid'):
                uid = event.uid
            data = {
                "uid": uid,
                "title": event.name,
                "start": self.get_date_formatted(event.begin, event.all_day),
                "end": self.get_date_formatted(event.end, event.all_day),
                "location": event.location,
                "description": event.description
            }
            # Note that we return a formatted date for start and end here,
            # but a different format for self.event!
            _LOGGER.debug("Created event: '{}' uid: '{}' start: '{}' end: '{}'".format(data['title'], data['uid'], data['start'], data['end']))
            event_list.append(data)

        return event_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data."""
        c = Calendar(urlopen(self.url).read().decode())
        tempEvent = None
        for event in c.timeline.at(arrow.utcnow()):
            if event.all_day and not self.include_all_day:
                continue
            if tempEvent is None:
                tempEvent = event
            elif tempEvent.end > event.end:
                tempEvent = event

        if tempEvent is None:
            self.event = None
            return True

        self.event = {
            "summary": tempEvent.name,
            "start": self.get_hass_date(tempEvent.begin, tempEvent.all_day),
            "end": self.get_hass_date(tempEvent.end, tempEvent.all_day),
            "location": tempEvent.location,
            "description": tempEvent.description
        }
        # Note that we use get_hass_date for start and end, not just a plain formatted date!
        log_start = None
        log_end = None
        if tempEvent.all_day:
            log_start = self.event['start']['date']
            log_end = self.event['end']['date']
        else:
            log_start = self.event['start']['dateTime']
            log_end = self.event['end']['dateTime']
        _LOGGER.debug("Created self.event: '{}' start: '{}' end: '{}'".format(self.event['summary'], log_start, log_end))
        return True

    @staticmethod
    def get_date_formatted(arw, is_all_day):
        """ Return the formatted date"""
        # Note that all day events should have a time of 0, and the timezone
        # must be local.  The server probably has the timezone erroneously set
        # to UTC!
        if is_all_day:
            arw = arw.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='local')
            return arw.format('YYYY-MM-DD')

        return arw.isoformat()

    @staticmethod
    def get_hass_date(arw, is_all_day):
        """ Return the wrapped and formatted date"""
        if is_all_day:
            return { "date": ICSCalendarData.get_date_formatted(arw, is_all_day) }
        return { "dateTime": ICSCalendarData.get_date_formatted(arw, is_all_day) }
