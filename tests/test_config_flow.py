"""Test the ICSCalendarConfigFlow class."""

# import copy
# from unittest.mock import ANY, AsyncMock, Mock, patch
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
    CONF_USER_AGENT,
    DOMAIN,
    config_flow,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def ics_enable_custom_integrations(enable_custom_integrations):
    """Provide enable_custom_integrations fixture for HA."""
    yield


class TestICSCalendarConfigFlow:
    """Test ICSCalendarConfigFlow class."""

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
        # Arrange
        expected = "https://localhost/test%20calendar.ics"
        url = "https://localhost/test calendar.ics"

        # Act
        # Assert
        assert expected == config_flow.format_url(url)

    def test_format_url_works_for_template(self):
        """Test that format_url works with a URL that has a template."""
        # Arrange
        expected = "https://localhost/{year}/{month}test%20calendar.ics"
        url = "https://localhost/{year}/{month}test calendar.ics"

        # Act
        # Assert
        assert expected == config_flow.format_url(url)

    @pytest.mark.asyncio
    async def test_async_step_user_shows_form(self, hass) -> None:
        """Test that form is shown for async_step_user."""
        # Arrange
        expected = {
            "data_schema": config_flow.CALENDAR_NAME_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": False,
            "preview": None,
            "step_id": "user",
            "type": FlowResultType.FORM,
        }
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_user_errors_for_blank_name(self, hass) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_NAME: "	 "}
        )
        # Assert
        assert {CONF_NAME: "empty_name"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_user_errors_for_empty_name(self, hass) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_NAME: ""}
        )
        # Assert
        assert {CONF_NAME: "empty_name"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_user_moves_to_calendar_opts_step(
        self, hass
    ) -> None:
        """Test that async_step_user moves to next step."""
        # Arrange
        expected = {
            "data_schema": config_flow.CALENDAR_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": False,
            "preview": None,
            "step_id": "calendar_opts",
            "type": FlowResultType.FORM,
        }
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_NAME: "test_calendar"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts(self, hass) -> None:
        """Test that form is shown for async_step_calendar_opts."""
        # Arrange
        expected = {
            "data_schema": config_flow.CALENDAR_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": False,
            "preview": None,
            "step_id": "calendar_opts",
            "type": FlowResultType.FORM,
        }
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "calendar_opts"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_bad_exclude(
        self, hass
    ) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "calendar_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_EXCLUDE: "exclude_me"}
        )
        # Assert
        assert {CONF_EXCLUDE: "exclude_must_be_array"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_bad_include(
        self, hass
    ) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "calendar_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_INCLUDE: "include_me"}
        )
        # Assert
        assert {CONF_INCLUDE: "include_must_be_array"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_same_exclude_include(
        self, hass
    ) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "calendar_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"],
            user_input={
                CONF_EXCLUDE: "[exclude_me]",
                CONF_INCLUDE: "[exclude_me]",
            },
        )
        # Assert
        assert {CONF_EXCLUDE: "exclude_include_cannot_be_the_same"} == result[
            "errors"
        ]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_errors_for_bad_download_interval(
        self, hass
    ) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "calendar_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"],
            user_input={
                CONF_EXCLUDE: "",
                CONF_INCLUDE: "",
                CONF_DOWNLOAD_INTERVAL: 5,
            },
        )
        # Assert
        assert {
            CONF_DOWNLOAD_INTERVAL: "download_interval_too_small"
        } == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_calendar_opts_moves_to_connect_opts_step(
        self, hass
    ) -> None:
        """Test that async_step_user moves to next step."""
        # Arrange
        expected = {
            "data_schema": config_flow.CONNECT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "connect_opts",
            "type": FlowResultType.FORM,
        }
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "calendar_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"],
            user_input={
                CONF_EXCLUDE: "",
                CONF_INCLUDE: "",
                CONF_DOWNLOAD_INTERVAL: 15,
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_connect_opts(self, hass) -> None:
        """Test that form is shown for async_step_connect_opts."""
        # Arrange
        expected = {
            "data_schema": config_flow.CONNECT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "connect_opts",
            "type": FlowResultType.FORM,
        }
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "connect_opts"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_errors_for_blank_url(
        self, hass
    ) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "connect_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_URL: "	 "}
        )
        # Assert
        assert {CONF_URL: "empty_url"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_errors_for_empty_url(
        self, hass
    ) -> None:
        """Test that async_step_user returns an error for an empty name."""
        # Arrange
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "connect_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={CONF_URL: ""}
        )
        # Assert
        assert {CONF_URL: "empty_url"} == result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_moves_to_auth_opts_step(
        self, hass
    ) -> None:
        """Test that async_step_user moves to auth_opt step if auth required."""
        # Arrange
        expected = {
            "data_schema": config_flow.AUTH_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "auth_opts",
            "type": FlowResultType.FORM,
        }
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "connect_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"],
            user_input={
                CONF_URL: "https://localhost/test.ics",
                CONF_REQUIRES_AUTH: True,
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_moves_to_adv_connect_opts_step(
        self, hass
    ) -> None:
        """Test that async_step_connect_opts moves to adv_connect_opt step."""
        # Arrange
        expected = {
            "data_schema": config_flow.ADVANCED_CONNECT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "adv_connect_opts",
            "type": FlowResultType.FORM,
        }
        _result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "connect_opts"}
        )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"],
            user_input={
                CONF_URL: "https://localhost/test.ics",
                CONF_REQUIRES_AUTH: False,
                CONF_ADV_CONNECT_OPTS: True,
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_connect_opts_creates_entry(self, hass) -> None:
        """Test that async_step_connect_opts creates an entry."""
        # Arrange
        data = {
            CONF_NAME: "test calendar",
            CONF_URL: "https://localhost/test.ics",
            CONF_REQUIRES_AUTH: False,
            CONF_ADV_CONNECT_OPTS: False,
            CONF_DOWNLOAD_INTERVAL: 15,
            CONF_INCLUDE: "",
            CONF_EXCLUDE: "",
            CONF_DAYS: 1,
            CONF_INCLUDE_ALL_DAY: False,
            CONF_OFFSET_HOURS: 0,
            CONF_PARSER: "rie",
            CONF_PREFIX: "",
        }
        expected = {
            "context": {"source": "user"},
            "data": data,
            "description": None,
            "description_placeholders": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "minor_version": config_flow.ICSCalendarConfigFlow.MINOR_VERSION,
            "options": {},
            "result": ANY,
            "title": data[CONF_NAME],
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
            await hass.async_block_till_done()
            _result_name = await hass.config_entries.flow.async_configure(
                _result["flow_id"],
                user_input={CONF_NAME: data[CONF_NAME]},
            )
            _result_cal_opts = await hass.config_entries.flow.async_configure(
                _result_name["flow_id"],
                user_input={
                    CONF_EXCLUDE: data[CONF_EXCLUDE],
                    CONF_INCLUDE: data[CONF_INCLUDE],
                    CONF_DOWNLOAD_INTERVAL: data[CONF_DOWNLOAD_INTERVAL],
                },
            )

        # Act
        result = await hass.config_entries.flow.async_configure(
            _result_cal_opts["flow_id"],
            user_input={
                CONF_URL: data[CONF_URL],
                CONF_REQUIRES_AUTH: data[CONF_REQUIRES_AUTH],
                CONF_ADV_CONNECT_OPTS: data[CONF_ADV_CONNECT_OPTS],
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_auth_opts(self, hass) -> None:
        """Test that form is shown for async_step_auth_opts."""
        # Arrange
        expected = {
            "data_schema": config_flow.AUTH_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "auth_opts",
            "type": FlowResultType.FORM,
        }
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "auth_opts"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_auth_opts_moves_to_adv_connect_opts_step(
        self, hass
    ) -> None:
        """Test that async_step_auth_opts moves to adv_connect_opts step."""
        # Arrange
        data = {
            CONF_NAME: "test calendar",
            CONF_URL: "https://localhost/test.ics",
            CONF_REQUIRES_AUTH: True,
            CONF_ADV_CONNECT_OPTS: True,
            CONF_DOWNLOAD_INTERVAL: 15,
            CONF_INCLUDE: "",
            CONF_EXCLUDE: "",
            CONF_DAYS: 1,
            CONF_INCLUDE_ALL_DAY: False,
            CONF_OFFSET_HOURS: 0,
            CONF_PARSER: "rie",
            CONF_PREFIX: "",
        }
        expected = {
            "data_schema": config_flow.ADVANCED_CONNECT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "adv_connect_opts",
            "type": FlowResultType.FORM,
        }
        with patch(
            "custom_components.ics_calendar.async_setup_entry",
            return_value=True,
        ):
            _result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "user"}
            )
            await hass.async_block_till_done()
            _result_name = await hass.config_entries.flow.async_configure(
                _result["flow_id"],
                user_input={CONF_NAME: data[CONF_NAME]},
            )
            _result_cal_opts = await hass.config_entries.flow.async_configure(
                _result_name["flow_id"],
                user_input={
                    CONF_EXCLUDE: data[CONF_EXCLUDE],
                    CONF_INCLUDE: data[CONF_INCLUDE],
                    CONF_DOWNLOAD_INTERVAL: data[CONF_DOWNLOAD_INTERVAL],
                },
            )
            _result_url_opts = await hass.config_entries.flow.async_configure(
                _result_cal_opts["flow_id"],
                user_input={
                    CONF_URL: data[CONF_URL],
                    CONF_REQUIRES_AUTH: data[CONF_REQUIRES_AUTH],
                    CONF_ADV_CONNECT_OPTS: data[CONF_ADV_CONNECT_OPTS],
                },
            )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result_url_opts["flow_id"],
            user_input={
                CONF_USERNAME: "username",
                CONF_PASSWORD: "password",
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_auth_opts_creates_entry(self, hass) -> None:
        """Test that async_step_auth_opts creates an entry."""
        # Arrange
        data = {
            CONF_NAME: "test calendar",
            CONF_URL: "https://localhost/test.ics",
            CONF_REQUIRES_AUTH: True,
            CONF_ADV_CONNECT_OPTS: False,
            CONF_DOWNLOAD_INTERVAL: 15,
            CONF_INCLUDE: "",
            CONF_EXCLUDE: "",
            CONF_DAYS: 1,
            CONF_INCLUDE_ALL_DAY: False,
            CONF_OFFSET_HOURS: 0,
            CONF_PARSER: "rie",
            CONF_PREFIX: "",
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        }
        expected = {
            "context": {"source": "user"},
            "data": data,
            "description": None,
            "description_placeholders": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "minor_version": config_flow.ICSCalendarConfigFlow.MINOR_VERSION,
            "options": {},
            "result": ANY,
            "title": data[CONF_NAME],
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
            await hass.async_block_till_done()
            _result_name = await hass.config_entries.flow.async_configure(
                _result["flow_id"],
                user_input={CONF_NAME: data[CONF_NAME]},
            )
            _result_cal_opts = await hass.config_entries.flow.async_configure(
                _result_name["flow_id"],
                user_input={
                    CONF_EXCLUDE: data[CONF_EXCLUDE],
                    CONF_INCLUDE: data[CONF_INCLUDE],
                    CONF_DOWNLOAD_INTERVAL: data[CONF_DOWNLOAD_INTERVAL],
                },
            )
            _result_url_opts = await hass.config_entries.flow.async_configure(
                _result_cal_opts["flow_id"],
                user_input={
                    CONF_URL: data[CONF_URL],
                    CONF_REQUIRES_AUTH: data[CONF_REQUIRES_AUTH],
                    CONF_ADV_CONNECT_OPTS: data[CONF_ADV_CONNECT_OPTS],
                },
            )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result_url_opts["flow_id"],
            user_input={
                CONF_USERNAME: data[CONF_USERNAME],
                CONF_PASSWORD: data[CONF_PASSWORD],
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_adv_connect_opts(self, hass) -> None:
        """Test that form is shown for async_step_adv_connect_opts."""
        # Arrange
        expected = {
            "data_schema": config_flow.ADVANCED_CONNECT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": None,
            "preview": None,
            "step_id": "adv_connect_opts",
            "type": FlowResultType.FORM,
        }
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "adv_connect_opts"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_adv_connect_opts_moves_to_timeout_step(
        self, hass
    ) -> None:
        """Test that async_step_auth_opts moves to adv_connect_opts step."""
        # Arrange
        data = {
            CONF_NAME: "test calendar",
            CONF_URL: "https://localhost/test.ics",
            CONF_SET_TIMEOUT: True,
            CONF_REQUIRES_AUTH: False,
            CONF_ADV_CONNECT_OPTS: True,
            CONF_DOWNLOAD_INTERVAL: 15,
            CONF_INCLUDE: "",
            CONF_EXCLUDE: "",
            CONF_DAYS: 1,
            CONF_INCLUDE_ALL_DAY: False,
            CONF_OFFSET_HOURS: 0,
            CONF_PARSER: "rie",
            CONF_PREFIX: "",
            CONF_USER_AGENT: "user-agent",
            CONF_ACCEPT_HEADER: "accept",
            CONF_SET_TIMEOUT: True,
        }
        expected = {
            "data_schema": config_flow.TIMEOUT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": True,
            "preview": None,
            "step_id": "timeout_opts",
            "type": FlowResultType.FORM,
        }
        with patch(
            "custom_components.ics_calendar.async_setup_entry",
            return_value=True,
        ):
            _result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "user"}
            )
            await hass.async_block_till_done()
            _result_name = await hass.config_entries.flow.async_configure(
                _result["flow_id"],
                user_input={CONF_NAME: data[CONF_NAME]},
            )
            _result_cal_opts = await hass.config_entries.flow.async_configure(
                _result_name["flow_id"],
                user_input={
                    CONF_EXCLUDE: data[CONF_EXCLUDE],
                    CONF_INCLUDE: data[CONF_INCLUDE],
                    CONF_DOWNLOAD_INTERVAL: data[CONF_DOWNLOAD_INTERVAL],
                },
            )
            _result_url_opts = await hass.config_entries.flow.async_configure(
                _result_cal_opts["flow_id"],
                user_input={
                    CONF_URL: data[CONF_URL],
                    CONF_REQUIRES_AUTH: data[CONF_REQUIRES_AUTH],
                    CONF_ADV_CONNECT_OPTS: data[CONF_ADV_CONNECT_OPTS],
                },
            )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result_url_opts["flow_id"],
            user_input={
                CONF_ACCEPT_HEADER: data[CONF_ACCEPT_HEADER],
                CONF_USER_AGENT: data[CONF_USER_AGENT],
                CONF_SET_TIMEOUT: data[CONF_SET_TIMEOUT],
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_adv_connect_opts_creates_entry(
        self, hass
    ) -> None:
        """Test that async_step_adv_connect_opts creates an entry."""
        # Arrange
        data = {
            CONF_NAME: "test calendar",
            CONF_URL: "https://localhost/test.ics",
            CONF_REQUIRES_AUTH: False,
            CONF_ADV_CONNECT_OPTS: True,
            CONF_DOWNLOAD_INTERVAL: 15,
            CONF_INCLUDE: "",
            CONF_EXCLUDE: "",
            CONF_DAYS: 1,
            CONF_INCLUDE_ALL_DAY: False,
            CONF_OFFSET_HOURS: 0,
            CONF_PARSER: "rie",
            CONF_PREFIX: "",
            CONF_USER_AGENT: "user-agent",
            CONF_ACCEPT_HEADER: "accept",
            CONF_SET_TIMEOUT: False,
        }
        expected = {
            "context": {"source": "user"},
            "data": data,
            "description": None,
            "description_placeholders": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "minor_version": config_flow.ICSCalendarConfigFlow.MINOR_VERSION,
            "options": {},
            "result": ANY,
            "title": data[CONF_NAME],
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
            await hass.async_block_till_done()
            _result_name = await hass.config_entries.flow.async_configure(
                _result["flow_id"],
                user_input={CONF_NAME: data[CONF_NAME]},
            )
            _result_cal_opts = await hass.config_entries.flow.async_configure(
                _result_name["flow_id"],
                user_input={
                    CONF_EXCLUDE: data[CONF_EXCLUDE],
                    CONF_INCLUDE: data[CONF_INCLUDE],
                    CONF_DOWNLOAD_INTERVAL: data[CONF_DOWNLOAD_INTERVAL],
                },
            )
            _result_url_opts = await hass.config_entries.flow.async_configure(
                _result_cal_opts["flow_id"],
                user_input={
                    CONF_URL: data[CONF_URL],
                    CONF_REQUIRES_AUTH: data[CONF_REQUIRES_AUTH],
                    CONF_ADV_CONNECT_OPTS: data[CONF_ADV_CONNECT_OPTS],
                },
            )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result_url_opts["flow_id"],
            user_input={
                CONF_ACCEPT_HEADER: data[CONF_ACCEPT_HEADER],
                CONF_USER_AGENT: data[CONF_USER_AGENT],
                CONF_SET_TIMEOUT: data[CONF_SET_TIMEOUT],
            },
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_timeout_opts(self, hass) -> None:
        """Test that form is shown for async_step_timeout_opts."""
        # Arrange
        expected = {
            "data_schema": config_flow.TIMEOUT_OPTS_SCHEMA,
            "description_placeholders": None,
            "errors": {},
            "flow_id": ANY,
            "handler": DOMAIN,
            "last_step": True,
            "preview": None,
            "step_id": "timeout_opts",
            "type": FlowResultType.FORM,
        }
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "timeout_opts"}
        )
        # Assert
        assert expected == result

    @pytest.mark.asyncio
    async def test_async_step_timeout_opts_creates_entry(self, hass) -> None:
        """Test that async_step_timeout_opts creates an entry."""
        # Arrange
        data = {
            CONF_NAME: "test calendar",
            CONF_URL: "https://localhost/test.ics",
            CONF_REQUIRES_AUTH: False,
            CONF_ADV_CONNECT_OPTS: True,
            CONF_DOWNLOAD_INTERVAL: 15,
            CONF_INCLUDE: "",
            CONF_EXCLUDE: "",
            CONF_DAYS: 1,
            CONF_INCLUDE_ALL_DAY: False,
            CONF_OFFSET_HOURS: 0,
            CONF_PARSER: "rie",
            CONF_PREFIX: "",
            CONF_USER_AGENT: "user-agent",
            CONF_ACCEPT_HEADER: "accept",
            CONF_SET_TIMEOUT: True,
            CONF_CONNECTION_TIMEOUT: 50,
        }
        expected = {
            "context": {"source": "user"},
            "data": data,
            "description": None,
            "description_placeholders": None,
            "flow_id": ANY,
            "handler": DOMAIN,
            "minor_version": config_flow.ICSCalendarConfigFlow.MINOR_VERSION,
            "options": {},
            "result": ANY,
            "title": data[CONF_NAME],
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
            await hass.async_block_till_done()
            _result_name = await hass.config_entries.flow.async_configure(
                _result["flow_id"],
                user_input={CONF_NAME: data[CONF_NAME]},
            )
            _result_cal_opts = await hass.config_entries.flow.async_configure(
                _result_name["flow_id"],
                user_input={
                    CONF_EXCLUDE: data[CONF_EXCLUDE],
                    CONF_INCLUDE: data[CONF_INCLUDE],
                    CONF_DOWNLOAD_INTERVAL: data[CONF_DOWNLOAD_INTERVAL],
                },
            )
            _result_url_opts = await hass.config_entries.flow.async_configure(
                _result_cal_opts["flow_id"],
                user_input={
                    CONF_URL: data[CONF_URL],
                    CONF_REQUIRES_AUTH: data[CONF_REQUIRES_AUTH],
                    CONF_ADV_CONNECT_OPTS: data[CONF_ADV_CONNECT_OPTS],
                },
            )
            _result_adv_opts = await hass.config_entries.flow.async_configure(
                _result_url_opts["flow_id"],
                user_input={
                    CONF_ACCEPT_HEADER: data[CONF_ACCEPT_HEADER],
                    CONF_USER_AGENT: data[CONF_USER_AGENT],
                    CONF_SET_TIMEOUT: data[CONF_SET_TIMEOUT],
                },
            )
        # Act
        result = await hass.config_entries.flow.async_configure(
            _result_adv_opts["flow_id"],
            user_input={
                CONF_CONNECTION_TIMEOUT: data[CONF_CONNECTION_TIMEOUT],
            },
        )
        # Assert
        assert expected == result
