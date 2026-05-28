"""ics Calendar for Home Assistant."""

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
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
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import discovery
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
)
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_ACCEPT_HEADER,
    CONF_ADV_CONNECT_OPTS,
    CONF_CALENDARS,
    CONF_CONNECTION_TIMEOUT,
    CONF_DAYS,
    CONF_DOWNLOAD_INTERVAL,
    CONF_INCLUDE_ALL_DAY,
    CONF_OFFSET_HOURS,
    CONF_PARSER,
    CONF_REQUIRES_AUTH,
    CONF_SET_TIMEOUT,
    CONF_SUMMARY_DEFAULT,
    CONF_SUMMARY_DEFAULT_DEFAULT,
    CONF_USER_AGENT,
    DOMAIN,
    STORAGE_VERSION_MAJOR,
    STORAGE_VERSION_MINOR,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.CALENDAR]

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
                                        CONF_CONNECTION_TIMEOUT, default=300
                                    ): cv.positive_float,
                                    vol.Optional(
                                        CONF_SUMMARY_DEFAULT,
                                        default=CONF_SUMMARY_DEFAULT_DEFAULT,
                                    ): cv.string,
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

STORAGE_KEY = DOMAIN

_DEFAULT_OPTIONS = {
    CONF_URL: "",
    CONF_ADV_CONNECT_OPTS: False,
    CONF_SET_TIMEOUT: False,
    CONF_REQUIRES_AUTH: False,
    CONF_INCLUDE_ALL_DAY: False,
    CONF_USERNAME: "",
    CONF_PASSWORD: "",
    CONF_PARSER: "rie",
    CONF_PREFIX: "",
    CONF_DAYS: 1,
    CONF_DOWNLOAD_INTERVAL: 15,
    CONF_USER_AGENT: "",
    CONF_EXCLUDE: "",
    CONF_INCLUDE: "",
    CONF_OFFSET_HOURS: 0,
    CONF_ACCEPT_HEADER: "",
    CONF_CONNECTION_TIMEOUT: 300.0,
    CONF_SUMMARY_DEFAULT: CONF_SUMMARY_DEFAULT_DEFAULT,
}


def _has_auth(values: dict) -> bool:
    """Return True if either credential field holds a non-empty value."""
    return bool(values.get(CONF_USERNAME)) or bool(values.get(CONF_PASSWORD))


def _has_custom_timeout(values: dict) -> bool:
    """Return True if CONNECTION_TIMEOUT is set to a non-default value."""
    timeout = values.get(CONF_CONNECTION_TIMEOUT)
    return timeout is not None and timeout != 300.0


def _has_adv_opts(values: dict) -> bool:
    """Return True if any advanced-connection field is set."""
    return (
        bool(values.get(CONF_USER_AGENT))
        or bool(values.get(CONF_ACCEPT_HEADER))
        or bool(values.get(CONF_SET_TIMEOUT))
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up calendars."""
    _LOGGER.debug("Setting up ics_calendar component")
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN in config and config[DOMAIN]:
        _LOGGER.debug("discovery.load_platform called")
        discovery.load_platform(
            hass=hass,
            component=PLATFORMS[0],
            platform=DOMAIN,
            discovered=config[DOMAIN],
            hass_config=config,
        )
        async_create_issue(
            hass,
            DOMAIN,
            "deprecated_yaml_configuration",
            is_fixable=False,
            issue_domain=DOMAIN,
            severity=IssueSeverity.WARNING,
            translation_key="YAML_Warning",
        )
        _LOGGER.warning(
            "YAML configuration of ics_calendar is deprecated and will be "
            "removed in ics_calendar v5.0.0. Your configuration items have "
            "been imported. Please remove them from your configuration.yaml "
            "file."
        )

        config_entry = _async_find_matching_config_entry(hass)
        if not config_entry:
            if config[DOMAIN].get("calendars"):
                for calendar in config[DOMAIN].get("calendars"):
                    hass.async_create_task(
                        hass.config_entries.flow.async_init(
                            DOMAIN,
                            context={"source": SOURCE_IMPORT},
                            data=dict(calendar),
                        )
                    )
            return True

        # update entry with any changes
        if config[DOMAIN].get("calendars"):
            for calendar in config[DOMAIN].get("calendars"):
                hass.config_entries.async_update_entry(
                    config_entry, data=dict(calendar)
                )

    return True


@callback
def _async_find_matching_config_entry(hass):
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.source == SOURCE_IMPORT:
            return entry
    return None


def _migrate_v1_0_to_v1_1(old_data: dict) -> tuple[dict, dict]:
    """Return (new_data, new_options) for the 1.0 → 1.1 migration.

    The UI-gating flags are recomputed from actual values rather than
    carried over, because pre-1.1 entries may have stored flag values that
    no longer reflect their actual settings.
    """
    new_options = {k: v for k, v in old_data.items() if k != CONF_NAME}
    new_data = {CONF_NAME: old_data.get(CONF_NAME, "")}
    new_options[CONF_REQUIRES_AUTH] = _has_auth(new_options)
    new_options[CONF_SET_TIMEOUT] = _has_custom_timeout(new_options)
    new_options[CONF_ADV_CONNECT_OPTS] = _has_adv_opts(new_options)
    return new_data, new_options


async def async_migrate_entry(hass, entry: ConfigEntry):
    """Migrate old config entry."""
    if entry.version > STORAGE_VERSION_MAJOR:
        return False
    if entry.version == STORAGE_VERSION_MAJOR and entry.minor_version < 1:
        new_data, new_options = _migrate_v1_0_to_v1_1(entry.data)
        hass.config_entries.async_update_entry(
            entry,
            data=new_data,
            options=new_options,
            minor_version=STORAGE_VERSION_MINOR,
            version=STORAGE_VERSION_MAJOR,
        )
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Implement async_setup_entry."""
    full_data: dict = add_missing_defaults(entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = full_data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


def add_missing_defaults(entry: ConfigEntry) -> dict:
    """Merge data & options on top of defaults.

    Derive any flags absent from the actual values.
    """
    data = {CONF_NAME: "", **_DEFAULT_OPTIONS}
    data.update(entry.data)
    data.update(entry.options)
    if CONF_REQUIRES_AUTH not in entry.options and _has_auth(data):
        data[CONF_REQUIRES_AUTH] = True
    if CONF_SET_TIMEOUT not in entry.options and _has_custom_timeout(data):
        data[CONF_SET_TIMEOUT] = True
    if CONF_ADV_CONNECT_OPTS not in entry.options and _has_adv_opts(data):
        data[CONF_ADV_CONNECT_OPTS] = True
    return data


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
