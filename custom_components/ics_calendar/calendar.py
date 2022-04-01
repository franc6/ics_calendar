"""Support for ICS Calendar."""
from calendar import Calendar
import copy
import logging
from datetime import datetime, timedelta

import voluptuous as vol
from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    CalendarEventDevice,
    extract_offset,
    get_date,
    is_offset_reached,
)
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_URL, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util import Throttle
from homeassistant.util.dt import now as hanow
from .icalendarparser import ICalendarParser
from .calendardata import CalendarData

VERSION = "2.0.0"

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = "device_id"
CONF_CALENDARS = "calendars"
CONF_DAYS = "days"
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
                            vol.Optional(CONF_PARSER, default="rie"): cv.string,
                            vol.Optional(CONF_DAYS, default=1): cv.positive_int,
                        }
                    )
                ]
            ),
        )
    }
)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
# MIN_TIME_BETWEEN_DOWNLOADS is smaller than MIN_TIME_BETWEEN_UPDATES so that
# it won't be skipped if an explicit update is called.  Eventually, if these
# are configurable, we'll let end users worry about if they mean to have it
# happen that way.
MIN_TIME_BETWEEN_DOWNLOADS = timedelta(minutes=10)


def setup_platform(hass, config, add_entities, _=None):
    """Set up the ICS Calendar platform"""
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
            CONF_DAYS: calendar.get(CONF_DAYS),
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
    def event(self):
        """Returns the current event for the calendar entity or None"""
        return self._event

    @property
    def name(self):
        """Returns the name of the calendar entity"""
        return self._name

    @property
    def should_poll(self):
        if (
            self._last_event_list is None
            or self._last_call is None
            or (hanow() - self._last_call) > MIN_TIME_BETWEEN_UPDATES
        ):
            self.async_schedule_update_ha_state(True)
        return True

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        if (
            self._last_event_list is None
            or self._last_call is None
            or (hanow() - self._last_call) > MIN_TIME_BETWEEN_UPDATES
        ):
            self._last_call = hanow()
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
        [summary, offset] = extract_offset(event["summary"], OFFSET)
        event["summary"] = summary
        self._event = event
        self._attr_extra_state_attributes = {
            "offset_reached": is_offset_reached(get_date(event["start"]), offset)
        }


class ICSCalendarData:
    """Calss to use the calendar ICS client object to get next event."""

    def __init__(self, device_data):
        """Set up how we are going to connect to the ICS Calendar"""
        self.name = device_data[CONF_NAME]
        self._days = device_data[CONF_DAYS]
        self.include_all_day = device_data[CONF_INCLUDE_ALL_DAY]
        self.parser = ICalendarParser.get_instance(device_data[CONF_PARSER])
        self.event = None
        self._calendar_data = CalendarData(
            _LOGGER, self.name, device_data[CONF_URL], MIN_TIME_BETWEEN_DOWNLOADS
        )

        if device_data[CONF_USERNAME] != "" and device_data[CONF_PASSWORD] != "":
            self._calendar_data.setUserNameAndPassword(
                device_data[CONF_USERNAME], device_data[CONF_PASSWORD]
            )

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        event_list = []
        await hass.async_add_executor_job(self._calendar_data.get)
        try:
            events = self.parser.get_event_list(
                content=self._calendar_data.get(),
                start=start_date,
                end=end_date,
                include_all_day=self.include_all_day,
            )
            event_list = list(map(self.format_dates, events))
        except:
            _LOGGER.error(
                f"async_get_events: {self.name}: Failed to parse ICS!", exc_info=True
            )
            event_list = []

        return event_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data."""
        _LOGGER.debug("update:")
        _LOGGER.debug(hanow())
        try:
            self.event = self.parser.get_current_event(
                content=self._calendar_data.get(),
                include_all_day=self.include_all_day,
                now=hanow(),
                days=self._days,
            )
        except:
            _LOGGER.error(f"update: {self.name}: Failed to parse ICS!", exc_info=True)
        if self.event is not None:
            _LOGGER.debug(
                f'{self.name}: got event: {self.event["summary"]};'
                f'start: {self.event["start"]}; end: {self.event["end"]};'
                f'all_day: {self.event["all_day"]}'
            )
            self.event["start"] = self.get_hass_date(
                self.event["start"], self.event["all_day"]
            )
            self.event["end"] = self.get_hass_date(
                self.event["end"], self.event["all_day"]
            )
            return True
        else:
            _LOGGER.debug(f"{self.name}: No event found!")

        return False

    def format_dates(self, event):
        event["start"] = self.get_date_formatted(event["start"], event["all_day"])
        event["end"] = self.get_date_formatted(event["end"], event["all_day"])
        return event

    def get_date_formatted(self, dt, is_all_day):
        """Return the formatted date"""
        # Note that all day events should have a time of 0, and the timezone
        # must be local.
        if is_all_day:
            return dt.strftime("%Y-%m-%d")

        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    def get_hass_date(self, dt, is_all_day):
        """Return the wrapped and formatted date"""
        if is_all_day:
            return {"date": self.get_date_formatted(dt, is_all_day)}
        return {"dateTime": self.get_date_formatted(dt, is_all_day)}
