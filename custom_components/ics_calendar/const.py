"""Constants for ics_calendar platform."""

VERSION = "5.1.6"
DOMAIN = "ics_calendar"

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
CONF_SET_TIMEOUT = "set_connection_timeout"
CONF_REQUIRES_AUTH = "requires_auth"
CONF_ADV_CONNECT_OPTS = "advanced_connection_options"
CONF_SUMMARY_DEFAULT = "summary_default"
# It'd be really nifty if this could be a translatable string, but it seems
# that's not supported, unless I want to roll my own interpretation of the
# translate/*.json files. :(
# See also https://github.com/home-assistant/core/issues/125075
CONF_SUMMARY_DEFAULT_DEFAULT = "No title"
