"""Support for ICS Calendar."""
import logging
from datetime import datetime, timedelta
from typing import Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    CalendarEntity,
    CalendarEvent,
    extract_offset,
    is_offset_reached,
)
from homeassistant.const import (
    CONF_EXCLUDE,
    CONF_INCLUDE,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import Throttle
from homeassistant.util.dt import now as hanow

from .calendardata import CalendarData
from .filter import Filter
from .icalendarparser import ICalendarParser

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = "device_id"
CONF_CALENDARS = "calendars"
CONF_DAYS = "days"
CONF_CALENDAR = "calendar"
CONF_INCLUDE_ALL_DAY = "include_all_day"
CONF_PARSER = "parser"
CONF_DOWNLOAD_INTERVAL = "download_interval"
CONF_USER_AGENT = "user_agent"
CONF_OFFSET_HOURS = "offset_hours"
CONF_ACCEPT_HEADER = "accept_header"

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
                            vol.Optional(
                                CONF_PARSER, default="rie"
                            ): cv.string,
                            vol.Optional(
                                CONF_DAYS, default=1
                            ): cv.positive_int,
                            vol.Optional(
                                CONF_DOWNLOAD_INTERVAL, default=15
                            ): cv.positive_int,
                            vol.Optional(
                                CONF_USER_AGENT, default=""
                            ): cv.string,
                            vol.Optional(CONF_EXCLUDE, default=""): cv.string,
                            vol.Optional(CONF_INCLUDE, default=""): cv.string,
                            vol.Optional(CONF_OFFSET_HOURS, default=0): int,
                            vol.Optional(
                                CONF_ACCEPT_HEADER, default=""
                            ): cv.string,
                        }
                    )
                ]
            ),
        )
    }
)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    _=None,
):
    """Set up ics_calendar platform.

    :param hass: Home Assistant object
    :type hass: HomeAssistant
    :param config: Config information for the platform
    :type config: ConfigType
    :param add_entities: Callback to add entities to HA
    :type add_entities: AddEntitiesCallback
    :param _: DiscoveryInfo, not used
    :type _: DiscoveryInfoType | None, optional
    """
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
            CONF_DOWNLOAD_INTERVAL: calendar.get(CONF_DOWNLOAD_INTERVAL),
            CONF_USER_AGENT: calendar.get(CONF_USER_AGENT),
            CONF_EXCLUDE: calendar.get(CONF_EXCLUDE),
            CONF_INCLUDE: calendar.get(CONF_INCLUDE),
            CONF_OFFSET_HOURS: calendar.get(CONF_OFFSET_HOURS),
            CONF_ACCEPT_HEADER: calendar.get(CONF_ACCEPT_HEADER),
        }
        device_id = f"{device_data[CONF_NAME]}"
        entity_id = generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        calendar_devices.append(ICSCalendarEntity(entity_id, device_data))

    add_entities(calendar_devices)


class ICSCalendarEntity(CalendarEntity):
    """A CalendarEntity for an ICS Calendar."""

    def __init__(self, entity_id: str, device_data):
        """Construct ICSCalendarEntity.

        :param entity_id: Entity id for the calendar
        :type entity_id: str
        :param device_data: dict describing the calendar
        :type device_data: dict
        """
        _LOGGER.debug(
            "Initializing calendar: %s with URL: %s",
            device_data[CONF_NAME],
            device_data[CONF_URL],
        )
        self.data = ICSCalendarData(device_data)
        self.entity_id = entity_id
        self._event = None
        self._name = device_data[CONF_NAME]
        self._last_call = None
        self._unique_id = device_data[CONF_URL]

    @property
    def event(self) -> Optional[CalendarEvent]:
        """Return the current event for the calendar entity or None.

        :return: The current event as a dict
        :rtype: dict
        """
        return self._event

    @property
    def name(self):
        """Return the name of the calendar."""
        return self._name
    
    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def should_poll(self):
        """Indicate if the calendar should be polled.

        If the last call to update or get_api_events was not within the minimum
        update time, then async_schedule_update_ha_state(True) is also called.
        :return: True
        :rtype: boolean
        """
        this_call = hanow()
        if (
            self._last_call is None
            or (this_call - self._last_call) > MIN_TIME_BETWEEN_UPDATES
        ):
            self._last_call = this_call
            self.async_schedule_update_ha_state(True)
        return True

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame.

        :param hass: Home Assistant object
        :type hass: HomeAssistant
        :param start_date: The first starting date to consider
        :type start_date: datetime
        :param end_date: The last starting date to consider
        :type end_date: datetime
        """
        _LOGGER.debug(
            "%s: async_get_events called; calling internal.", self.name
        )
        return await self.data.async_get_events(hass, start_date, end_date)

    def update(self):
        """Get the current or next event."""
        self.data.update()
        self._event = self.data.event
        self._attr_extra_state_attributes = {
            "offset_reached": is_offset_reached(
                self._event.start_datetime_local, self.data.offset
            )
            if self._event
            else False
        }


class ICSCalendarData:
    """Class to use the calendar ICS client object to get next event."""

    def __init__(self, device_data):
        """Set up how we are going to connect to the URL.

        :param device_data Information about the calendar
        """
        self.name = device_data[CONF_NAME]
        self._days = device_data[CONF_DAYS]
        self._offset_hours = device_data[CONF_OFFSET_HOURS]
        self.include_all_day = device_data[CONF_INCLUDE_ALL_DAY]
        self.parser = ICalendarParser.get_instance(device_data[CONF_PARSER])
        self.parser.set_filter(
            Filter(device_data[CONF_EXCLUDE], device_data[CONF_INCLUDE])
        )
        self.offset = None
        self.event = None

        self._calendar_data = CalendarData(
            _LOGGER,
            self.name,
            device_data[CONF_URL],
            timedelta(minutes=device_data[CONF_DOWNLOAD_INTERVAL]),
        )

        self._calendar_data.set_headers(
            device_data[CONF_USERNAME],
            device_data[CONF_PASSWORD],
            device_data[CONF_USER_AGENT],
            device_data[CONF_ACCEPT_HEADER],
        )

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame.

        :param hass: Home Assistant object
        :type hass: HomeAssistant
        :param start_date: The first starting date to consider
        :type start_date: datetime
        :param end_date: The last starting date to consider
        :type end_date: datetime
        """
        event_list = []
        if await hass.async_add_executor_job(
            self._calendar_data.download_calendar
        ):
            _LOGGER.debug("%s: Setting calendar content", self.name)
            self.parser.set_content(self._calendar_data.get())
        try:
            event_list = self.parser.get_event_list(
                start=start_date,
                end=end_date,
                include_all_day=self.include_all_day,
                offset_hours=self._offset_hours,
            )
        except:  # pylint: disable=W0702
            _LOGGER.error(
                "async_get_events: %s: Failed to parse ICS!",
                self.name,
                exc_info=True,
            )
            event_list = []

        return event_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the current or next event."""
        _LOGGER.debug("%s: Update was called", self.name)
        if self._calendar_data.download_calendar():
            _LOGGER.debug("%s: Setting calendar content", self.name)
            self.parser.set_content(self._calendar_data.get())
        try:
            self.event = self.parser.get_current_event(
                include_all_day=self.include_all_day,
                now=hanow(),
                days=self._days,
                offset_hours=self._offset_hours,
            )
        except:  # pylint: disable=W0702
            _LOGGER.error(
                "update: %s: Failed to parse ICS!", self.name, exc_info=True
            )
        if self.event is not None:
            _LOGGER.debug(
                "%s: got event: %s; start: %s; end: %s; all_day: %s",
                self.name,
                self.event.summary,
                self.event.start,
                self.event.end,
                self.event.all_day,
            )
            (summary, offset) = extract_offset(self.event.summary, OFFSET)
            self.event.summary = summary
            self.offset = offset
            return True

        _LOGGER.debug("%s: No event found!", self.name)
        return False
