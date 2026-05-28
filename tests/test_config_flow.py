"""Test the ICSCalendarConfigFlow and ICSCalendarOptionsFlow classes."""

from unittest.mock import ANY, patch

import pytest
from homeassistant.const import (
    CONF_EXCLUDE,
    CONF_INCLUDE,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PREFIX,
    CONF_URL,
    CONF_USERNAME,
)
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ics_calendar import (
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
    DOMAIN,
    config_flow,
)
from custom_components.ics_calendar.const import CONF_SUMMARY_DEFAULT_DEFAULT

pytest_plugins = "pytest_homeassistant_custom_component"

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_DEFAULT_CAL_OPTS = {
    CONF_DAYS: 1,
    CONF_INCLUDE_ALL_DAY: False,
    CONF_EXCLUDE: "",
    CONF_INCLUDE: "",
    CONF_PREFIX: "",
    CONF_DOWNLOAD_INTERVAL: 15,
    CONF_OFFSET_HOURS: 0,
    CONF_PARSER: "rie",
    CONF_SUMMARY_DEFAULT: CONF_SUMMARY_DEFAULT_DEFAULT,
}

_DEFAULT_CONNECT_OPTS = {
    CONF_URL: "https://localhost/test.ics",
    CONF_REQUIRES_AUTH: False,
    CONF_ADV_CONNECT_OPTS: False,
}


async def _create_config_entry(hass, name="test calendar"):
    """Create a config entry by completing the config flow."""
    with patch(
        "custom_components.ics_calendar.async_setup_entry",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_NAME: name}
        )
        await hass.async_block_till_done()
    return result["result"]


async def _init_options_flow(hass, entry):
    """Initialize the options flow for the given config entry."""
    return await hass.config_entries.options.async_init(entry.entry_id)


async def _advance_cal_opts(hass, flow_id, overrides=None):
    """Submit calendar_opts step with default valid input."""
    user_input = dict(_DEFAULT_CAL_OPTS)
    if overrides:
        user_input.update(overrides)
    return await hass.config_entries.options.async_configure(
        flow_id, user_input=user_input
    )


async def _advance_connect_opts(hass, flow_id, overrides=None):
    """Submit connect_opts step with default valid input."""
    user_input = dict(_DEFAULT_CONNECT_OPTS)
    if overrides:
        user_input.update(overrides)
    return await hass.config_entries.options.async_configure(
        flow_id, user_input=user_input
    )


def _schema_defaults(data_schema):
    """Return a {field_name: default_value} dict for a voluptuous Schema."""
    return {
        str(key): key.default()
        for key in data_schema.schema
        if hasattr(key, "default") and key.default is not None
    }


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def ics_enable_custom_integrations(enable_custom_integrations):
    """Provide enable_custom_integrations fixture for HA."""
    yield


# ---------------------------------------------------------------------------
# Config flow tests
# ---------------------------------------------------------------------------


class TestICSCalendarConfigFlow:
    """Test ICSCalendarConfigFlow class."""

    # ------------------------------------------------------------------
    # Pure-function tests (format_url, is_array_string)
    # ------------------------------------------------------------------

    def test_is_array_string_returns_true_if_array_string(self) -> None:
        """Test that is_array_string returns true correctly."""
        assert config_flow.is_array_string("[]")
        assert config_flow.is_array_string("[ item ]")
        assert config_flow.is_array_string("[ item1, item2 ]")

    def test_is_array_string_returns_true_if_not_array_string(self) -> None:
        """Test that is_array_string returns false correctly."""
        assert False is config_flow.is_array_string("[")
        assert False is config_flow.is_array_string("item")
        assert False is config_flow.is_array_string("item1, item2")
        assert False is config_flow.is_array_string(" [ item1, item2 ] ")

    def test_format_url_works(self):
        """Test that format_url works with a generic URL."""
        expected = "https://localhost/test%20calendar.ics"
        url = "https://localhost/test calendar.ics"
        assert expected == config_flow.format_url(url)

    def test_format_url_works_for_template(self):
        """Test that format_url works with a URL that has a template."""
        expected = "https://localhost/{year}/{month}test%20calendar.ics"
        url = "https://localhost/{year}/{month}test calendar.ics"
        assert expected == config_flow.format_url(url)

    def test_format_url_works_for_template_offset(self):
        """Test that format_url works with a URL that has a template."""
        expected = "https://localhost/{year-1}/{month+1}test%20calendar.ics"
        url = "https://localhost/{year-1}/{month+1}test calendar.ics"
        assert expected == config_flow.format_url(url)

    def test_format_url_works_if_encoded(self):
        """Test that format_url works with a URL that is already encoded."""
        expected = "https://localhost/test%20calendar.ics"
        url = "https://localhost/test%20calendar.ics"
        assert expected == config_flow.format_url(url)

    def test_format_url_works_for_template_if_encoded(self):
        """Test that format_url works with an encoded URL that has a template."""
        expected = "https://localhost/{year}/{month}test%20calendar.ics"
        assert expected == config_flow.format_url(expected)

    def test_format_changes_webcal_to_https(self):
        """Test that format_url converts webcal:// to https://."""
        expected = "https://localhost/{year}/{month}test%20calendar.ics"
        url = "webcal://localhost/{year}/{month}test%20calendar.ics"
        assert expected == config_flow.format_url(url)

    # ------------------------------------------------------------------
    # async_step_user: form display
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_async_step_user_shows_form(self, hass) -> None:
        """Test that form is shown for async_step_user."""
        expected = {
            "data_schema": config_flow.CALENDAR_NAME_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": True,
            "preview": None,
            "step_id": "user",
            "type": FlowResultType.FORM,
        }
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_user_errors_for_blank_name(self, hass) -> None:
        """Test that async_step_user returns an error for a whitespace-only name."""
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_NAME: "	 "}
        )
        assert {CONF_NAME: "empty_name"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_user_errors_for_empty_name(self, hass) -> None:
        """Test that async_step_user returns an error for an empty name."""
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_NAME: ""}
        )
        assert {CONF_NAME: "empty_name"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_user_creates_entry(self, hass) -> None:
        """Test that async_step_user creates an entry (name in data, empty options)."""
        name = "test_calendar"
        expected = {
            "context": {"source": "user"},
            "data": {CONF_NAME: name},
            "description": None,
            "description_placeholders": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "minor_version": config_flow.ICSCalendarConfigFlow.MINOR_VERSION,
            "options": {},
            "result": ANY,
            "subentries": (),
            "title": name,
            "type": FlowResultType.CREATE_ENTRY,
            "version": config_flow.ICSCalendarConfigFlow.VERSION,
        }
        with patch(
            "custom_components.ics_calendar.async_setup_entry",
            return_value=True,
        ):
            _result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "user"}
            )
            result = await hass.config_entries.flow.async_configure(
                _result["flow_id"], user_input={CONF_NAME: name}
            )
        assert expected == result


# ---------------------------------------------------------------------------
# Options flow tests
# ---------------------------------------------------------------------------


class TestICSCalendarOptionsFlow:
    """Test ICSCalendarOptionsFlow class."""

    # ------------------------------------------------------------------
    # calendar_opts step
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_async_step_init_shows_calendar_opts_form(
        self, hass
    ) -> None:
        """Test that the options flow starts at the calendar_opts step."""
        entry = await _create_config_entry(hass)
        result = await _init_options_flow(hass, entry)
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "calendar_opts"
        assert result["errors"] == {}
        assert result["last_step"] is False
        assert result["description_placeholders"] == {
            "filterdoc": config_flow.FILTER_DOC_URL
        }

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_bad_exclude(
        self, hass
    ) -> None:
        """Test that calendar_opts returns an error for a non-array exclude."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={**_DEFAULT_CAL_OPTS, CONF_EXCLUDE: "exclude_me"},
        )
        assert {CONF_EXCLUDE: "exclude_must_be_array"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_bad_include(
        self, hass
    ) -> None:
        """Test that calendar_opts returns an error for a non-array include."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={**_DEFAULT_CAL_OPTS, CONF_INCLUDE: "include_me"},
        )
        assert {CONF_INCLUDE: "include_must_be_array"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_same_exclude_include(
        self, hass
    ) -> None:
        """Test that calendar_opts returns an error when exclude equals include."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={
                **_DEFAULT_CAL_OPTS,
                CONF_EXCLUDE: "[exclude_me]",
                CONF_INCLUDE: "[exclude_me]",
            },
        )
        assert {CONF_EXCLUDE: "exclude_include_cannot_be_the_same"} == result[
            "errors"
        ]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_bad_download_interval(
        self, hass
    ) -> None:
        """Test that calendar_opts returns an error for a download_interval < 15."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={**_DEFAULT_CAL_OPTS, CONF_DOWNLOAD_INTERVAL: 5},
        )
        assert {
            CONF_DOWNLOAD_INTERVAL: "download_interval_too_small"
        } == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_moves_to_connect_opts_step(
        self, hass
    ) -> None:
        """Test that calendar_opts advances to the connect_opts step."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        result = await _advance_cal_opts(hass, _result["flow_id"])
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "connect_opts"
        assert result["errors"] == {}

    # ------------------------------------------------------------------
    # connect_opts step
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_errors_for_blank_url(
        self, hass
    ) -> None:
        """Test that connect_opts returns an error for a whitespace-only URL."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"], user_input={CONF_URL: "	 "}
        )
        assert {CONF_URL: "empty_url"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_errors_for_empty_url(
        self, hass
    ) -> None:
        """Test that connect_opts returns an error for an empty URL."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"], user_input={CONF_URL: ""}
        )
        assert {CONF_URL: "empty_url"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_moves_to_auth_opts_step(
        self, hass
    ) -> None:
        """Test that connect_opts advances to auth_opts when requires_auth is True."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        result = await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_REQUIRES_AUTH: True},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "auth_opts"

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_moves_to_adv_connect_opts_step(
        self, hass
    ) -> None:
        """Test that connect_opts advances to adv_connect_opts when adv_opts is True."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        result = await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_ADV_CONNECT_OPTS: True},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "adv_connect_opts"

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_creates_entry(self, hass) -> None:
        """Test that connect_opts creates an entry (no auth, no adv opts)."""
        expected_options = {
            **_DEFAULT_CAL_OPTS,
            **_DEFAULT_CONNECT_OPTS,
        }
        entry = await _create_config_entry(hass)
        with (
            patch(
                "custom_components.ics_calendar.async_setup_entry",
                return_value=True,
            ),
            patch(
                "custom_components.ics_calendar.async_unload_entry",
                return_value=True,
            ),
        ):
            _result = await _init_options_flow(hass, entry)
            await _advance_cal_opts(hass, _result["flow_id"])
            result = await _advance_connect_opts(hass, _result["flow_id"])
            await hass.async_block_till_done()
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == expected_options

    # ------------------------------------------------------------------
    # auth_opts step
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_async_step_auth_opts_shows_form(self, hass) -> None:
        """Test that auth_opts form is shown when requires_auth is True."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        result = await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_REQUIRES_AUTH: True},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "auth_opts"
        assert result["errors"] is None

    @pytest.mark.asyncio
    async def test_async_step_auth_opts_moves_to_adv_connect_opts_step(
        self, hass
    ) -> None:
        """Test that auth_opts advances to adv_connect_opts when adv_opts is True."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_REQUIRES_AUTH: True, CONF_ADV_CONNECT_OPTS: True},
        )
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={CONF_USERNAME: "username", CONF_PASSWORD: "password"},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "adv_connect_opts"

    @pytest.mark.asyncio
    async def test_async_step_auth_opts_creates_entry(self, hass) -> None:
        """Test that auth_opts creates an entry when adv_opts is False."""
        expected_options = {
            **_DEFAULT_CAL_OPTS,
            **_DEFAULT_CONNECT_OPTS,
            CONF_REQUIRES_AUTH: True,
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        }
        entry = await _create_config_entry(hass)
        with (
            patch(
                "custom_components.ics_calendar.async_setup_entry",
                return_value=True,
            ),
            patch(
                "custom_components.ics_calendar.async_unload_entry",
                return_value=True,
            ),
        ):
            _result = await _init_options_flow(hass, entry)
            await _advance_cal_opts(hass, _result["flow_id"])
            await _advance_connect_opts(
                hass,
                _result["flow_id"],
                overrides={
                    CONF_REQUIRES_AUTH: True,
                    CONF_ADV_CONNECT_OPTS: False,
                },
            )
            result = await hass.config_entries.options.async_configure(
                _result["flow_id"],
                user_input={
                    CONF_USERNAME: "username",
                    CONF_PASSWORD: "password",
                },
            )
            await hass.async_block_till_done()
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == expected_options

    @pytest.mark.asyncio
    async def test_async_step_auth_opts_creates_entry_with_empty_summary(
        self, hass
    ) -> None:
        """Test that auth_opts substitutes the default for an empty summary."""
        expected_options = {
            **_DEFAULT_CAL_OPTS,
            CONF_SUMMARY_DEFAULT: CONF_SUMMARY_DEFAULT_DEFAULT,
            **_DEFAULT_CONNECT_OPTS,
            CONF_REQUIRES_AUTH: True,
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        }
        entry = await _create_config_entry(hass)
        with (
            patch(
                "custom_components.ics_calendar.async_setup_entry",
                return_value=True,
            ),
            patch(
                "custom_components.ics_calendar.async_unload_entry",
                return_value=True,
            ),
        ):
            _result = await _init_options_flow(hass, entry)
            await _advance_cal_opts(
                hass,
                _result["flow_id"],
                overrides={CONF_SUMMARY_DEFAULT: ""},
            )
            await _advance_connect_opts(
                hass,
                _result["flow_id"],
                overrides={
                    CONF_REQUIRES_AUTH: True,
                    CONF_ADV_CONNECT_OPTS: False,
                },
            )
            result = await hass.config_entries.options.async_configure(
                _result["flow_id"],
                user_input={
                    CONF_USERNAME: "username",
                    CONF_PASSWORD: "password",
                },
            )
            await hass.async_block_till_done()
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == expected_options

    # ------------------------------------------------------------------
    # adv_connect_opts step
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_async_step_adv_connect_opts_shows_form(self, hass) -> None:
        """Test that adv_connect_opts form is shown when adv_opts is True."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        result = await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_ADV_CONNECT_OPTS: True},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "adv_connect_opts"
        assert result["errors"] == {}

    @pytest.mark.asyncio
    async def test_async_step_adv_connect_opts_moves_to_timeout_step(
        self, hass
    ) -> None:
        """Test that adv_connect_opts advances to timeout_opts when set_timeout."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_ADV_CONNECT_OPTS: True},
        )
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={
                CONF_ACCEPT_HEADER: "accept",
                CONF_USER_AGENT: "user-agent",
                CONF_SET_TIMEOUT: True,
            },
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "timeout_opts"
        assert result["last_step"] is True

    @pytest.mark.asyncio
    async def test_async_step_adv_connect_opts_creates_entry(
        self, hass
    ) -> None:
        """Test that adv_connect_opts creates an entry when set_timeout is False."""
        expected_options = {
            **_DEFAULT_CAL_OPTS,
            **_DEFAULT_CONNECT_OPTS,
            CONF_ADV_CONNECT_OPTS: True,
            CONF_ACCEPT_HEADER: "accept",
            CONF_USER_AGENT: "user-agent",
            CONF_SET_TIMEOUT: False,
        }
        entry = await _create_config_entry(hass)
        with (
            patch(
                "custom_components.ics_calendar.async_setup_entry",
                return_value=True,
            ),
            patch(
                "custom_components.ics_calendar.async_unload_entry",
                return_value=True,
            ),
        ):
            _result = await _init_options_flow(hass, entry)
            await _advance_cal_opts(hass, _result["flow_id"])
            await _advance_connect_opts(
                hass,
                _result["flow_id"],
                overrides={CONF_ADV_CONNECT_OPTS: True},
            )
            result = await hass.config_entries.options.async_configure(
                _result["flow_id"],
                user_input={
                    CONF_ACCEPT_HEADER: "accept",
                    CONF_USER_AGENT: "user-agent",
                    CONF_SET_TIMEOUT: False,
                },
            )
            await hass.async_block_till_done()
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == expected_options

    # ------------------------------------------------------------------
    # timeout_opts step
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_async_step_timeout_opts_shows_form(self, hass) -> None:
        """Test that timeout_opts form is shown when set_timeout is True."""
        entry = await _create_config_entry(hass)
        _result = await _init_options_flow(hass, entry)
        await _advance_cal_opts(hass, _result["flow_id"])
        await _advance_connect_opts(
            hass,
            _result["flow_id"],
            overrides={CONF_ADV_CONNECT_OPTS: True},
        )
        await hass.config_entries.options.async_configure(
            _result["flow_id"],
            user_input={
                CONF_ACCEPT_HEADER: "",
                CONF_USER_AGENT: "",
                CONF_SET_TIMEOUT: True,
            },
        )
        result = await hass.config_entries.options.async_configure(
            _result["flow_id"], user_input=None
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "timeout_opts"
        assert result["last_step"] is True

    @pytest.mark.asyncio
    async def test_async_step_timeout_opts_creates_entry(self, hass) -> None:
        """Test that timeout_opts creates an entry with the connection timeout."""
        expected_options = {
            **_DEFAULT_CAL_OPTS,
            **_DEFAULT_CONNECT_OPTS,
            CONF_ADV_CONNECT_OPTS: True,
            CONF_ACCEPT_HEADER: "accept",
            CONF_USER_AGENT: "user-agent",
            CONF_SET_TIMEOUT: True,
            CONF_CONNECTION_TIMEOUT: 50.0,
        }
        entry = await _create_config_entry(hass)
        with (
            patch(
                "custom_components.ics_calendar.async_setup_entry",
                return_value=True,
            ),
            patch(
                "custom_components.ics_calendar.async_unload_entry",
                return_value=True,
            ),
        ):
            _result = await _init_options_flow(hass, entry)
            await _advance_cal_opts(hass, _result["flow_id"])
            await _advance_connect_opts(
                hass,
                _result["flow_id"],
                overrides={CONF_ADV_CONNECT_OPTS: True},
            )
            await hass.config_entries.options.async_configure(
                _result["flow_id"],
                user_input={
                    CONF_ACCEPT_HEADER: "accept",
                    CONF_USER_AGENT: "user-agent",
                    CONF_SET_TIMEOUT: True,
                },
            )
            result = await hass.config_entries.options.async_configure(
                _result["flow_id"],
                user_input={CONF_CONNECTION_TIMEOUT: 50.0},
            )
            await hass.async_block_till_done()
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == expected_options

    # ------------------------------------------------------------------
    # Pre-population tests — verify existing options appear as defaults
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_calendar_opts_form_pre_populates_existing_options(
        self, hass
    ) -> None:
        """Test that calendar_opts form fields show current option values."""
        from pytest_homeassistant_custom_component.common import (
            MockConfigEntry,
        )

        existing_options = {
            CONF_DAYS: 7,
            CONF_INCLUDE_ALL_DAY: True,
            CONF_EXCLUDE: "[exclude]",
            CONF_INCLUDE: "[include]",
            CONF_PREFIX: "PREFIX ",
            CONF_DOWNLOAD_INTERVAL: 30,
            CONF_OFFSET_HOURS: 2,
            CONF_PARSER: "ics",
            CONF_SUMMARY_DEFAULT: "custom default",
            CONF_URL: "https://existing.example.com/cal.ics",
        }
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_NAME: "pre-pop test"},
            options=existing_options,
        )
        entry.add_to_hass(hass)
        result = await _init_options_flow(hass, entry)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "calendar_opts"
        defaults = _schema_defaults(result["data_schema"])
        expected_defaults = {
            "days": 7,
            "include_all_day": True,
            "exclude": "[exclude]",
            "include": "[include]",
            "prefix": "PREFIX ",
            "download_interval": 30,
            "offset_hours": 2,
            "summary_default": "custom default",
        }
        for field, value in expected_defaults.items():
            assert defaults.get(field) == value, f"{field} default mismatch"

    @pytest.mark.asyncio
    async def test_connect_opts_form_pre_populates_existing_url(
        self, hass
    ) -> None:
        """Test that connect_opts form pre-populates the URL from existing options."""
        from pytest_homeassistant_custom_component.common import (
            MockConfigEntry,
        )

        existing_options = {
            **_DEFAULT_CAL_OPTS,
            CONF_URL: "https://existing.example.com/cal.ics",
            CONF_REQUIRES_AUTH: False,
            CONF_ADV_CONNECT_OPTS: False,
        }
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_NAME: "pre-pop test"},
            options=existing_options,
        )
        entry.add_to_hass(hass)
        _result = await _init_options_flow(hass, entry)
        result = await _advance_cal_opts(hass, _result["flow_id"])

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "connect_opts"
        schema = result["data_schema"]
        schema_defaults = {
            str(key): key.default()
            for key in schema.schema
            if hasattr(key, "default") and key.default is not None
        }
        assert (
            schema_defaults.get("url")
            == "https://existing.example.com/cal.ics"
        )


# ---------------------------------------------------------------------------
# async_migrate_entry tests
# ---------------------------------------------------------------------------


class TestAsyncMigrateEntry:
    """Test that async_migrate_entry moves a 1.0-shaped entry to 1.1."""

    @staticmethod
    def _migrate(hass, data):
        """Build a 1.0 entry from data and run the migration."""
        from pytest_homeassistant_custom_component.common import (
            MockConfigEntry,
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data=data,
            options={},
            version=1,
            minor_version=0,
        )
        entry.add_to_hass(hass)
        return entry

    @pytest.mark.asyncio
    async def test_migrate_moves_data_fields_into_options(self, hass) -> None:
        """A 1.0 entry (everything in data) becomes a 1.1 entry (name in data, rest in options)."""
        from custom_components.ics_calendar import async_migrate_entry

        old_data = {
            CONF_NAME: "migrated calendar",
            CONF_URL: "https://old.example.com/cal.ics",
            CONF_DAYS: 3,
            CONF_INCLUDE_ALL_DAY: True,
            CONF_DOWNLOAD_INTERVAL: 20,
            CONF_PARSER: "ics",
        }
        entry = self._migrate(hass, old_data)

        assert await async_migrate_entry(hass, entry) is True

        assert entry.data == {CONF_NAME: "migrated calendar"}
        assert entry.options == {
            CONF_URL: "https://old.example.com/cal.ics",
            CONF_DAYS: 3,
            CONF_INCLUDE_ALL_DAY: True,
            CONF_DOWNLOAD_INTERVAL: 20,
            CONF_PARSER: "ics",
            CONF_REQUIRES_AUTH: False,
            CONF_SET_TIMEOUT: False,
            CONF_ADV_CONNECT_OPTS: False,
        }
        assert entry.minor_version == 1

    @pytest.mark.asyncio
    async def test_migrate_resets_flags_for_default_values(self, hass) -> None:
        """Empty credentials and the default 300.0 timeout reset the flags to False."""
        from custom_components.ics_calendar import async_migrate_entry

        old_data = {
            CONF_NAME: "legacy calendar",
            CONF_URL: "https://old.example.com/cal.ics",
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
            CONF_USER_AGENT: "",
            CONF_ACCEPT_HEADER: "",
            CONF_CONNECTION_TIMEOUT: 300.0,
            CONF_REQUIRES_AUTH: True,
            CONF_SET_TIMEOUT: True,
            CONF_ADV_CONNECT_OPTS: True,
        }
        entry = self._migrate(hass, old_data)

        assert await async_migrate_entry(hass, entry) is True

        assert entry.options[CONF_REQUIRES_AUTH] is False
        assert entry.options[CONF_SET_TIMEOUT] is False
        assert entry.options[CONF_ADV_CONNECT_OPTS] is False

    @pytest.mark.asyncio
    async def test_migrate_preserves_real_auth(self, hass) -> None:
        """A 1.0 entry that genuinely has auth (non-empty USERNAME) keeps REQUIRES_AUTH True."""
        from custom_components.ics_calendar import async_migrate_entry

        old_data = {
            CONF_NAME: "auth calendar",
            CONF_URL: "https://old.example.com/cal.ics",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_REQUIRES_AUTH: True,
        }
        entry = self._migrate(hass, old_data)

        assert await async_migrate_entry(hass, entry) is True

        assert entry.options[CONF_REQUIRES_AUTH] is True
        assert entry.options[CONF_SET_TIMEOUT] is False
        assert entry.options[CONF_ADV_CONNECT_OPTS] is False

    @pytest.mark.asyncio
    async def test_migrate_preserves_real_timeout(self, hass) -> None:
        """A 1.0 entry with a custom (non-300) timeout keeps SET_TIMEOUT and ADV_CONNECT_OPTS True."""
        from custom_components.ics_calendar import async_migrate_entry

        old_data = {
            CONF_NAME: "timeout calendar",
            CONF_URL: "https://old.example.com/cal.ics",
            CONF_CONNECTION_TIMEOUT: 45.0,
            CONF_SET_TIMEOUT: True,
            CONF_ADV_CONNECT_OPTS: True,
        }
        entry = self._migrate(hass, old_data)

        assert await async_migrate_entry(hass, entry) is True

        assert entry.options[CONF_REQUIRES_AUTH] is False
        assert entry.options[CONF_SET_TIMEOUT] is True
        assert entry.options[CONF_ADV_CONNECT_OPTS] is True

    @pytest.mark.asyncio
    async def test_migrate_preserves_custom_user_agent(self, hass) -> None:
        """A 1.0 entry with a custom USER_AGENT keeps ADV_CONNECT_OPTS True only."""
        from custom_components.ics_calendar import async_migrate_entry

        old_data = {
            CONF_NAME: "ua calendar",
            CONF_URL: "https://old.example.com/cal.ics",
            CONF_USER_AGENT: "Mozilla/5.0",
            CONF_ADV_CONNECT_OPTS: True,
        }
        entry = self._migrate(hass, old_data)

        assert await async_migrate_entry(hass, entry) is True

        assert entry.options[CONF_REQUIRES_AUTH] is False
        assert entry.options[CONF_SET_TIMEOUT] is False
        assert entry.options[CONF_ADV_CONNECT_OPTS] is True


# ---------------------------------------------------------------------------
# add_missing_defaults tests
# ---------------------------------------------------------------------------


class TestAddMissingDefaults:
    """Test that add_missing_defaults derives flags from values when absent."""

    @staticmethod
    def _entry(options):
        from pytest_homeassistant_custom_component.common import (
            MockConfigEntry,
        )

        return MockConfigEntry(
            domain=DOMAIN,
            data={CONF_NAME: "test"},
            options=options,
        )

    def test_derives_requires_auth_from_yaml_import(self):
        """YAML-import-shaped entry (no flag in options, USERNAME set) derives True."""
        from custom_components.ics_calendar import add_missing_defaults

        entry = self._entry(
            {CONF_URL: "https://example.com/cal.ics", CONF_USERNAME: "user"}
        )
        data = add_missing_defaults(entry)
        assert data[CONF_REQUIRES_AUTH] is True

    def test_does_not_override_explicit_false_flag(self):
        """Migrated entry (flag explicitly False, empty USERNAME) keeps False."""
        from custom_components.ics_calendar import add_missing_defaults

        entry = self._entry(
            {
                CONF_URL: "https://example.com/cal.ics",
                CONF_REQUIRES_AUTH: False,
                CONF_USERNAME: "",
                CONF_PASSWORD: "",
            }
        )
        data = add_missing_defaults(entry)
        assert data[CONF_REQUIRES_AUTH] is False

    def test_default_timeout_does_not_derive_set_timeout(self):
        """A YAML import with the default 300.0 timeout does not trigger SET_TIMEOUT."""
        from custom_components.ics_calendar import add_missing_defaults

        entry = self._entry(
            {
                CONF_URL: "https://example.com/cal.ics",
                CONF_CONNECTION_TIMEOUT: 300.0,
            }
        )
        data = add_missing_defaults(entry)
        assert data[CONF_SET_TIMEOUT] is False
        assert data[CONF_ADV_CONNECT_OPTS] is False

    def test_custom_timeout_derives_flags(self):
        """A YAML import with a custom timeout derives SET_TIMEOUT and ADV_CONNECT_OPTS."""
        from custom_components.ics_calendar import add_missing_defaults

        entry = self._entry(
            {
                CONF_URL: "https://example.com/cal.ics",
                CONF_CONNECTION_TIMEOUT: 45.0,
            }
        )
        data = add_missing_defaults(entry)
        assert data[CONF_SET_TIMEOUT] is True
        assert data[CONF_ADV_CONNECT_OPTS] is True
