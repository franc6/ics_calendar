"""ics Calendar for Home Assistant."""

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
    CONF_EXCLUDE,
    CONF_INCLUDE,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PREFIX,
    CONF_URL,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, UPGRADE_URL

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.CALENDAR]

CONF_DEVICE_ID = "device_id"
CONF_CALENDARS = "calendars"
CONF_DAYS = "days"
CONF_INCLUDE_ALL_DAY = "include_all_day"
CONF_PARSER = "parser"
CONF_DOWNLOAD_INTERVAL = "download_interval"
CONF_USER_AGENT = "user_agent"
CONF_OFFSET_HOURS = "offset_hours"
CONF_ACCEPT_HEADER = "accept_header"
CONF_CONNECTION_TIMEOUT = "connection_timeout"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
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
                                    vol.Optional(
                                        CONF_USERNAME, default=""
                                    ): cv.string,
                                    vol.Optional(
                                        CONF_PASSWORD, default=""
                                    ): cv.string,
                                    vol.Optional(
                                        CONF_PARSER, default="rie"
                                    ): cv.string,
                                    vol.Optional(
                                        CONF_PREFIX, default=""
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
                                    vol.Optional(
                                        CONF_EXCLUDE, default=""
                                    ): cv.string,
                                    vol.Optional(
                                        CONF_INCLUDE, default=""
                                    ): cv.string,
                                    vol.Optional(
                                        CONF_OFFSET_HOURS, default=0
                                    ): int,
                                    vol.Optional(
                                        CONF_ACCEPT_HEADER, default=""
                                    ): cv.string,
                                    vol.Optional(
                                        CONF_CONNECTION_TIMEOUT, default=None
                                    ): cv.socket_timeout,
                                }
                            )
                        ]
                    ),
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up calendars."""
    _LOGGER.debug("Setting up ics_calendar component")
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN in config and config[DOMAIN]:
        hass.helpers.discovery.load_platform(
            PLATFORMS[0], DOMAIN, config[DOMAIN], config
        )
    else:
        _LOGGER.error(
            "No configuration found! If you upgraded from ics_calendar v3.2.0 "
            "or older, you need to update your configuration! See "
            "%s for more information.",
            UPGRADE_URL,
        )

    return True
