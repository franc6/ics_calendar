"""Provide CalendarData class."""
from datetime import timedelta
from logging import Logger
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.request import (
    HTTPBasicAuthHandler,
    HTTPDigestAuthHandler,
    HTTPPasswordMgrWithDefaultRealm,
    build_opener,
    install_opener,
    urlopen,
)

from homeassistant.util.dt import now as hanow


class CalendarData:
    """CalendarData class.

    The CalendarData class is used to download and cache calendar data from a
    given URL.  Use the get method to retrieve the data after constructing your
    instance.
    """

    def __init__(
        self, logger: Logger, name: str, url: str, min_update_time: timedelta
    ):
        """Construct CalendarData object.

        :param logger: The logger for reporting problems
        :type logger: Logger
        :param name: The name of the calendar (used for reporting problems)
        :type name: str
        :param url: The URL of the calendar
        :type url: str
        :param min_update_time: The minimum time between downloading data from
            the URL when requested
        :type min_update_time: timedelta
        """
        self._calendar_data = None
        self._last_download = None
        self._min_update_time = min_update_time
        self.logger = logger
        self.name = name
        self.url = url

    def _download_calendar(self):
        now = hanow()
        if (
            self._calendar_data is None
            or self._last_download is None
            or (now - self._last_download) > self._min_update_time
        ):
            self._last_download = now
            self._calendar_data = None
            try:
                with urlopen(self.url) as conn:
                    self._calendar_data = (
                        conn.read().decode().replace("\0", "")
                    )
            except HTTPError as http_error:
                self.logger.error(
                    "%s: Failed to open url: %s", self.name, http_error.reason
                )
            except ContentTooShortError as content_too_short_error:
                self.logger.error(
                    "%s: Could not download calendar data: %s",
                    self.name,
                    content_too_short_error.reason,
                )
            except URLError as url_error:
                self.logger.error(
                    "%s: Failed to open url: %s", self.name, url_error.reason
                )
            except:  # pylint: disable=W0702
                self.logger.error(
                    "%s: Failed to open url!", self.name, exc_info=True
                )

    def get(self) -> str:
        """Get the calendar data that was downloaded.

        :return: The downloaded calendar data; this may be cached data
        :rtype: str
        """
        self._download_calendar()
        return self._calendar_data

    def set_user_name_password(self, user_name: str, password: str):
        """Set a user name and password to use when downloading the calendar data.

        :param user_name: The user name
        :type user_name: str
        :param password: The password
        :type password: str
        """
        passman = HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.url, user_name, password)
        basic_auth_handler = HTTPBasicAuthHandler(passman)
        digest_auth_handler = HTTPDigestAuthHandler(passman)
        opener = build_opener(digest_auth_handler, basic_auth_handler)
        install_opener(opener)
