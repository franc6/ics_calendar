"""Config Flow for ICS Calendar."""

import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import quote

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_EXCLUDE,
    CONF_INCLUDE,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PREFIX,
    CONF_URL,
    CONF_USERNAME,
)
from homeassistant.helpers.selector import selector

from . import (
    CONF_ACCEPT_HEADER,
    CONF_ADV_CONNECT_OPTS,
    CONF_CONNECTION_TIMEOUT,
    CONF_DAYS,
    CONF_DOWNLOAD_INTERVAL,
    CONF_INCLUDE_ALL_DAY,
    CONF_OFFSET_HOURS,
    CONF_PARSER,
    CONF_REQUIRES_AUTH,
    CONF_SET_TIMEOUT,
    CONF_USER_AGENT,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CALENDAR_NAME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_DAYS, default=1): cv.positive_int,
        vol.Optional(CONF_INCLUDE_ALL_DAY, default=False): cv.boolean,
    }
)

CALENDAR_OPTS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_EXCLUDE, default=""): cv.string,
        vol.Optional(CONF_INCLUDE, default=""): cv.string,
        vol.Optional(CONF_PREFIX, default=""): cv.string,
        vol.Optional(CONF_DOWNLOAD_INTERVAL, default=15): cv.positive_int,
        vol.Optional(CONF_OFFSET_HOURS, default=0): int,
        vol.Optional(CONF_PARSER, default="rie"): selector(
            {"select": {"options": ["rie", "ics"], "mode": "dropdown"}}
        ),
    }
)

CONNECT_OPTS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Optional(CONF_REQUIRES_AUTH, default=False): cv.boolean,
        vol.Optional(CONF_ADV_CONNECT_OPTS, default=False): cv.boolean,
    }
)

AUTH_OPTS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_USERNAME, default=""): cv.string,
        vol.Optional(CONF_PASSWORD, default=""): cv.string,
    }
)

ADVANCED_CONNECT_OPTS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ACCEPT_HEADER, default=""): cv.string,
        vol.Optional(CONF_USER_AGENT, default=""): cv.string,
        vol.Optional(CONF_SET_TIMEOUT, default=False): cv.boolean,
    }
)

TIMEOUT_OPTS_SCHEMA = vol.Schema(
    {vol.Optional(CONF_CONNECTION_TIMEOUT, default=None): cv.positive_float}
)


def is_array_string(arr_str: str) -> bool:
    """Return true if arr_str starts with [ and ends with ]."""
    return arr_str.startswith("[") and arr_str.endswith("]")


def format_url(url: str) -> str:
    """Format a URL using quote() and ensure any templates are not quoted."""
    has_template = "{year}" in url or "{month}" in url
    url = quote(url, safe=":/?&=")
    if has_template:
        url = re.sub("%7[Bb]year%7[Dd]", "{year}", url)
        url = re.sub("%7[Bb]month%7[Dd]", "{month}", url)

    return url


class ICSCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config Flow for ICS Calendar."""

    VERSION = 1
    MINOR_VERSION = 0

    data: Optional[Dict[str, Any]]

    def __init__(self):
        """Construct ICSCalendarConfigFlow."""
        self.data = {}

    async def async_step_reauth(self, user_input=None):
        """Re-authenticateon auth error."""
        # self.reauth_entry = self.hass.config_entries.async_get_entry(
        # self.context["entry_id"]
        # )
        return await self.async_step_reauth_confirm(user_input)

    async def async_step_reauth_confirm(
        self, user_input=None
    ) -> ConfigFlowResult:
        """Dialog to inform user that reauthentication is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm", data_schema=vol.Schema({})
            )
        return await self.async_step_user()

    # Don't allow reconfigure for now!
    # async def async_step_reconfigure(
    #    self, user_input: dict[str, Any] | None = None
    # ) -> ConfigFlowResult:
    #    """Reconfigure entry."""
    #    return await self.async_step_user(user_input)

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Start of Config Flow."""
        errors = {}
        if user_input is not None:
            user_input[CONF_NAME] = user_input[CONF_NAME].strip()
            if not user_input[CONF_NAME]:
                errors[CONF_NAME] = "empty_name"
            else:
                self._async_abort_entries_match(
                    {CONF_NAME: user_input[CONF_NAME]}
                )

            if not errors:
                self.data = user_input
                return await self.async_step_calendar_opts()

        return self.async_show_form(
            step_id="user",
            data_schema=CALENDAR_NAME_SCHEMA,
            errors=errors,
            last_step=False,
        )

    async def async_step_calendar_opts(  # noqa: R701
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Calendar Options step for ConfigFlow."""
        errors = {}
        if user_input is not None:
            user_input[CONF_EXCLUDE] = user_input[CONF_EXCLUDE].strip()
            user_input[CONF_INCLUDE] = user_input[CONF_INCLUDE].strip()
            if (
                user_input[CONF_EXCLUDE]
                and user_input[CONF_EXCLUDE] == user_input[CONF_INCLUDE]
            ):
                errors[CONF_EXCLUDE] = "exclude_include_cannot_be_the_same"
            else:
                if user_input[CONF_EXCLUDE] and not is_array_string(
                    user_input[CONF_EXCLUDE]
                ):
                    errors[CONF_EXCLUDE] = "exclude_must_be_array"
                if user_input[CONF_INCLUDE] and not is_array_string(
                    user_input[CONF_INCLUDE]
                ):
                    errors[CONF_INCLUDE] = "include_must_be_array"

            if user_input[CONF_DOWNLOAD_INTERVAL] < 15:
                _LOGGER.error("download_interval_too_small error")
                errors[CONF_DOWNLOAD_INTERVAL] = "download_interval_too_small"

            if not errors:
                self.data.update(user_input)
                return await self.async_step_connect_opts()

        return self.async_show_form(
            step_id="calendar_opts",
            data_schema=CALENDAR_OPTS_SCHEMA,
            errors=errors,
            last_step=False,
        )

    async def async_step_connect_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Connect Options step for ConfigFlow."""
        errors = {}
        if user_input is not None:
            user_input[CONF_URL] = user_input[CONF_URL].strip()
            if not user_input[CONF_URL]:
                errors[CONF_URL] = "empty_url"

            if not errors:
                user_input[CONF_URL] = format_url(user_input[CONF_URL])

                self.data.update(user_input)
                if user_input.get(CONF_REQUIRES_AUTH, False):
                    return await self.async_step_auth_opts()
                if user_input.get(CONF_ADV_CONNECT_OPTS, False):
                    return await self.async_step_adv_connect_opts()
                return self.async_create_entry(
                    title=self.data[CONF_NAME],
                    data=self.data,
                )

        return self.async_show_form(
            step_id="connect_opts",
            data_schema=CONNECT_OPTS_SCHEMA,
            errors=errors,
        )

    async def async_step_auth_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Auth Options step for ConfigFlow."""
        if user_input is not None:
            self.data.update(user_input)
            if self.data.get(CONF_ADV_CONNECT_OPTS, False):
                return await self.async_step_adv_connect_opts()
            return self.async_create_entry(
                title=self.data[CONF_NAME],
                data=self.data,
            )

        return self.async_show_form(
            step_id="auth_opts", data_schema=AUTH_OPTS_SCHEMA
        )

    async def async_step_adv_connect_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Advanced Connection Options step for ConfigFlow."""
        errors = {}
        if user_input is not None:

            if not errors:
                self.data.update(user_input)
                if user_input.get(CONF_SET_TIMEOUT, False):
                    return await self.async_step_timeout_opts()
                return self.async_create_entry(
                    title=self.data[CONF_NAME],
                    data=self.data,
                )

        return self.async_show_form(
            step_id="adv_connect_opts",
            data_schema=ADVANCED_CONNECT_OPTS_SCHEMA,
            errors=errors,
        )

    async def async_step_timeout_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Timeout Options step for ConfigFlow."""
        errors = {}
        if user_input is not None:

            if not errors:
                self.data.update(user_input)
                return self.async_create_entry(
                    title=self.data[CONF_NAME],
                    data=self.data,
                )

        return self.async_show_form(
            step_id="timeout_opts",
            data_schema=TIMEOUT_OPTS_SCHEMA,
            errors=errors,
            last_step=True,
        )

    async def async_step_import(self, import_data):
        """Import config from configuration.yaml."""
        return self.async_create_entry(
            title=import_data[CONF_NAME],
            data=import_data,
        )
