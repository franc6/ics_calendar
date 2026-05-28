"""Config Flow for ICS Calendar."""

import logging
import re
from typing import Any, Dict, Optional, Self
from urllib.parse import quote

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
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
    CONF_SUMMARY_DEFAULT,
    CONF_USER_AGENT,
)
from .const import CONF_SUMMARY_DEFAULT_DEFAULT, DOMAIN

_LOGGER = logging.getLogger(__name__)

CALENDAR_NAME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
    }
)

FILTER_DOC_URL = (
    "https://github.com/franc6/ics_calendar/blob/releases/README.md#filters"
)


def is_array_string(arr_str: str) -> bool:
    """Return true if arr_str starts with [ and ends with ]."""
    return arr_str.startswith("[") and arr_str.endswith("]")


def format_url(url: str) -> str:
    """Format a URL using quote() and ensure any templates are not quoted."""
    is_quoted = bool(re.search("%[0-9A-Fa-f][0-9A-Fa-f]", url))
    if not is_quoted:
        year_match = re.search("\\{(year([-+][0-9]+)?)\\}", url)
        month_match = re.search("\\{(month([-+][0-9]+)?)\\}", url)
        has_template: bool = year_match or month_match
        url = quote(url, safe=":/?&=")
        if has_template:
            year_template = year_match.group(1)
            month_template = month_match.group(1)
            year_template1 = year_template.replace("+", "%2[Bb]")
            month_template1 = month_template.replace("+", "%2[Bb]")
            url = re.sub(
                f"%7[Bb]{year_template1}%7[Dd]",
                f"{{{year_template}}}",
                url,
            )
            url = re.sub(
                f"%7[Bb]{month_template1}%7[Dd]",
                f"{{{month_template}}}",
                url,
            )
    if url.startswith("webcal://"):
        url = re.sub("^webcal://", "https://", url)

    return url


def _calendar_opts_schema(options: dict) -> vol.Schema:
    """Build calendar options schema."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_DAYS, default=options.get(CONF_DAYS, 1)
            ): cv.positive_int,
            vol.Optional(
                CONF_INCLUDE_ALL_DAY,
                default=options.get(CONF_INCLUDE_ALL_DAY, False),
            ): cv.boolean,
            vol.Optional(
                CONF_EXCLUDE, default=options.get(CONF_EXCLUDE, "")
            ): cv.string,
            vol.Optional(
                CONF_INCLUDE, default=options.get(CONF_INCLUDE, "")
            ): cv.string,
            vol.Optional(
                CONF_PREFIX, default=options.get(CONF_PREFIX, "")
            ): cv.string,
            vol.Optional(
                CONF_DOWNLOAD_INTERVAL,
                default=options.get(CONF_DOWNLOAD_INTERVAL, 15),
            ): cv.positive_int,
            vol.Optional(
                CONF_OFFSET_HOURS, default=options.get(CONF_OFFSET_HOURS, 0)
            ): int,
            vol.Optional(
                CONF_PARSER, default=options.get(CONF_PARSER, "rie")
            ): selector(
                {"select": {"options": ["rie", "ics"], "mode": "dropdown"}}
            ),
            vol.Optional(
                CONF_SUMMARY_DEFAULT,
                default=options.get(
                    CONF_SUMMARY_DEFAULT, CONF_SUMMARY_DEFAULT_DEFAULT
                ),
            ): cv.string,
        }
    )


def _connect_opts_schema(options: dict) -> vol.Schema:
    """Build connection options schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_URL, default=options.get(CONF_URL, "")
            ): cv.string,
            vol.Optional(
                CONF_REQUIRES_AUTH,
                default=options.get(CONF_REQUIRES_AUTH, False),
            ): cv.boolean,
            vol.Optional(
                CONF_ADV_CONNECT_OPTS,
                default=options.get(CONF_ADV_CONNECT_OPTS, False),
            ): cv.boolean,
        }
    )


def _auth_opts_schema(options: dict) -> vol.Schema:
    """Build authentication options schema."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_USERNAME, default=options.get(CONF_USERNAME, "")
            ): cv.string,
            vol.Optional(
                CONF_PASSWORD, default=options.get(CONF_PASSWORD, "")
            ): cv.string,
        }
    )


def _adv_connect_opts_schema(options: dict) -> vol.Schema:
    """Build advanced connection options schema."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_ACCEPT_HEADER, default=options.get(CONF_ACCEPT_HEADER, "")
            ): cv.string,
            vol.Optional(
                CONF_USER_AGENT, default=options.get(CONF_USER_AGENT, "")
            ): cv.string,
            vol.Optional(
                CONF_SET_TIMEOUT, default=options.get(CONF_SET_TIMEOUT, False)
            ): cv.boolean,
        }
    )


def _timeout_opts_schema(options: dict) -> vol.Schema:
    """Build timeout options schema."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_CONNECTION_TIMEOUT,
                default=options.get(CONF_CONNECTION_TIMEOUT, None),
            ): cv.positive_float
        }
    )


class ICSCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config Flow for ICS Calendar."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self):
        """Construct ICSCalendarConfigFlow."""

    @staticmethod
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> "ICSCalendarOptionsFlow":
        """Get the options flow handler."""
        return ICSCalendarOptionsFlow(config_entry)

    def is_matching(self, _other_flow: Self) -> bool:
        """Match discovery method.

        This method doesn't do anything, because this integration has no
        discoverable components.
        """
        return False

    async def async_step_reauth(self, user_input=None):
        """Re-authentication on auth error."""
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
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={CONF_NAME: user_input[CONF_NAME]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=CALENDAR_NAME_SCHEMA,
            errors=errors,
            last_step=True,
        )

    async def async_step_import(self, import_data):
        """Import config from configuration.yaml."""
        name = import_data.get(CONF_NAME, "")
        options = {k: v for k, v in import_data.items() if k != CONF_NAME}
        return self.async_create_entry(
            title=name,
            data={CONF_NAME: name},
            options=options,
        )


class ICSCalendarOptionsFlow(OptionsFlow):
    """Options Flow for ICS Calendar."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize options flow."""
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Start of Options Flow."""
        return await self.async_step_calendar_opts(user_input)

    async def async_step_calendar_opts(  # noqa: R701,C901
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Calendar Options step for OptionsFlow."""
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

            if not user_input[CONF_SUMMARY_DEFAULT]:
                user_input[CONF_SUMMARY_DEFAULT] = CONF_SUMMARY_DEFAULT_DEFAULT

            if not errors:
                self.options.update(user_input)
                return await self.async_step_connect_opts()

        return self.async_show_form(
            step_id="calendar_opts",
            data_schema=_calendar_opts_schema(self.options),
            errors=errors,
            last_step=False,
            description_placeholders={"filterdoc": FILTER_DOC_URL},
        )

    async def async_step_connect_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Connect Options step for OptionsFlow."""
        errors = {}
        if user_input is not None:
            user_input[CONF_URL] = user_input[CONF_URL].strip()
            if not user_input[CONF_URL]:
                errors[CONF_URL] = "empty_url"

            if not errors:
                user_input[CONF_URL] = format_url(user_input[CONF_URL])

                self.options.update(user_input)
                if user_input.get(CONF_REQUIRES_AUTH, False):
                    return await self.async_step_auth_opts()
                if user_input.get(CONF_ADV_CONNECT_OPTS, False):
                    return await self.async_step_adv_connect_opts()
                return self.async_create_entry(data=self.options)

        return self.async_show_form(
            step_id="connect_opts",
            data_schema=_connect_opts_schema(self.options),
            errors=errors,
        )

    async def async_step_auth_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Auth Options step for OptionsFlow."""
        if user_input is not None:
            self.options.update(user_input)
            if self.options.get(CONF_ADV_CONNECT_OPTS, False):
                return await self.async_step_adv_connect_opts()
            return self.async_create_entry(data=self.options)

        return self.async_show_form(
            step_id="auth_opts",
            data_schema=_auth_opts_schema(self.options),
        )

    async def async_step_adv_connect_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Advanced Connection Options step for OptionsFlow."""
        errors = {}
        if user_input is not None:
            self.options.update(user_input)
            if user_input.get(CONF_SET_TIMEOUT, False):
                return await self.async_step_timeout_opts()
            return self.async_create_entry(data=self.options)

        return self.async_show_form(
            step_id="adv_connect_opts",
            data_schema=_adv_connect_opts_schema(self.options),
            errors=errors,
        )

    async def async_step_timeout_opts(
        self, user_input: Optional[Dict[str, Any]] = None
    ):
        """Timeout Options step for OptionsFlow."""
        errors = {}
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(data=self.options)

        return self.async_show_form(
            step_id="timeout_opts",
            data_schema=_timeout_opts_schema(self.options),
            errors=errors,
            last_step=True,
        )
