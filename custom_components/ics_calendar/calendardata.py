"""Provide CalendarData class."""

from datetime import timedelta
from logging import Logger
from socket import (  # type: ignore[attr-defined]  # private, not in typeshed
    _GLOBAL_DEFAULT_TIMEOUT,
)
from threading import Lock

import httpx
import httpx_auth
from homeassistant.util.dt import now as hanow

# from urllib.error import ContentTooShortError, HTTPError, URLError


class DigestWithMultiAuth(httpx.DigestAuth, httpx_auth.SupportMultiAuth):
    """Describes a DigestAuth authentication."""

    def __init__(self, username: str, password: str):
        """Construct Digest authentication that supports Multi Auth."""
        httpx.DigestAuth.__init__(self, username, password)


class CalendarData:  # pylint: disable=R0902
    """CalendarData class.

    The CalendarData class is used to download and cache calendar data from a
    given URL.  Use the get method to retrieve the data after constructing your
    instance.
    """

    # Allow only one download at a time globally
    download_singleton_lock = Lock()

    def __init__(  # pylint: disable=R0913,R0917
        self,
        async_client: httpx.AsyncClient,
        logger: Logger,
        name: str,
        url: str,
        min_update_time: timedelta,
    ):
        """Construct CalendarData object.

        :param async_client: An httpx.AsyncClient object for requests
        :type httpx.AsyncClient
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
        self._auth = None
        self._calendar_data = None
        self._headers = []
        self._last_download = None
        self._min_update_time = min_update_time
        self.logger = logger
        self.name = name
        self.url = url
        self.connection_timeout = _GLOBAL_DEFAULT_TIMEOUT
        self._httpx = async_client

    async def download_calendar(self) -> bool:
        """Download the calendar data.

        This only downloads data if self.min_update_time has passed since the
        last download.

        returns: True if data was downloaded, otherwise False.
        rtype: bool
        """
        self.logger.debug("%s: download_calendar start", self.name)
        with CalendarData.download_singleton_lock:
            self.logger.debug("%s: download_calendar lock acquired", self.name)
            if (
                self._calendar_data is None
                or self._last_download is None
                or (hanow() - self._last_download) > self._min_update_time
            ):
                self._calendar_data = None
                next_url: str = self._make_url()
                self.logger.debug(
                    "%s: Downloading calendar data from: %s",
                    self.name,
                    next_url,
                )
                await self._download_data(next_url)
                self._last_download = hanow()
                self.logger.debug("%s: download_calendar done", self.name)
                return self._calendar_data is not None

        self.logger.debug("%s: download_calendar skipped download", self.name)
        return False

    def get(self) -> str:
        """Get the calendar data that was downloaded.

        :return: The downloaded calendar data.
        :rtype: str
        """
        return self._calendar_data

    def set_headers(
        self,
        user_name: str,
        password: str,
        user_agent: str,
        accept_header: str,
    ):
        """Set a user agent, accept header, and/or user name and password.

        The user name and password will be set into an auth object that
        supports both Basic Auth and Digest Auth for httpx.

        If the user_agent parameter is not "", a User-agent header will be
        added to the urlopener.

        :param user_name: The user name
        :type user_name: str
        :param password: The password
        :type password: str
        :param user_agent: The User Agent string to use or ""
        :type user_agent: str
        :param accept_header: The accept header string to use or ""
        :type accept_header: str
        """
        if user_name != "" and password != "":
            self._auth = httpx_auth.Basic(
                user_name, password
            ) + DigestWithMultiAuth(user_name, password)

        if user_agent != "":
            self._headers.append(("User-agent", user_agent))
        if accept_header != "":
            self._headers.append(("Accept", accept_header))

    def set_timeout(self, connection_timeout: float):
        """Set the connection timeout.

        :param connection_timeout: The timeout value in seconds.
        :type connection_timeout: float
        """
        self.connection_timeout = connection_timeout

    def _decode_data(self, data):
        return data.replace("\0", "")

    async def _download_data(self, url):  # noqa: C901
        """Download the calendar data."""
        self.logger.debug("%s: _download_data start", self.name)
        try:
            response = await self._httpx.get(
                url,
                auth=self._auth,
                headers=self._headers,
                follow_redirects=True,
                timeout=self.connection_timeout,
            )
            if response.status_code >= 400:
                raise httpx.HTTPStatusError(
                    "status error", request=None, response=response
                )
            self._calendar_data = self._decode_data(response.text)
            self.logger.debug("%s: _download_data done", self.name)
        except httpx.HTTPStatusError as http_status_error:
            self.logger.error(
                "%s: Failed to open url(%s): %s",
                self.name,
                self.url,
                http_status_error.response.status_code,
            )
        except httpx.TimeoutException:
            self.logger.error(
                "%s: Timeout opening url: %s", self.name, self.url
            )
        except httpx.DecodingError:
            self.logger.error(
                "%s: Error decoding data from url: %s", self.name, self.url
            )
        except httpx.InvalidURL:
            self.logger.error("%s: Invalid URL: %s", self.name, self.url)
        except httpx.HTTPError:
            self.logger.error(
                "%s: Error decoding data from url: %s", self.name, self.url
            )
        except:  # pylint: disable=W0702
            self.logger.error(
                "%s: Failed to open url!", self.name, exc_info=True
            )

    def _make_url(self):
        """Replace templates in url and encode."""
        now = hanow()
        return self.url.replace("{year}", f"{now.year:04}").replace(
            "{month}", f"{now.month:02}"
        )
