"""Provide CalendarData class."""
import time
import zlib
from datetime import timedelta
from gzip import BadGzipFile, GzipFile
from logging import Logger
from random import uniform
from socket import (  # type: ignore[attr-defined]  # private, not in typeshed
    _GLOBAL_DEFAULT_TIMEOUT,
)
from threading import Lock
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


class CalendarData:  # pylint: disable=R0902
    """CalendarData class.

    The CalendarData class is used to download and cache calendar data from a
    given URL.  Use the get method to retrieve the data after constructing your
    instance.
    """

    opener_lock = Lock()

    def __init__(
        self,
        logger: Logger,
        name: str,
        url: str,
        min_update_time: timedelta,
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
        self._opener = None
        self.logger = logger
        self.name = name
        self.url = url
        self.connection_timeout = _GLOBAL_DEFAULT_TIMEOUT
        # set a random sleep between 0.001 seconds & 2.000 seconds to
        # reduce server load, particularly if lots of calendars all use the
        # same server.
        self._sleep_time = uniform(0.001, 2.000)

    def download_calendar(self) -> bool:
        """Download the calendar data.

        This only downloads data if self.min_update_time has passed since the
        last download.

        returns: True if data was downloaded, otherwise False.
        rtype: bool
        """
        now = hanow()
        if (
            self._calendar_data is None
            or self._last_download is None
            or (now - self._last_download) > self._min_update_time
        ):
            self._last_download = now
            self._calendar_data = None
            self.logger.debug(
                "%s: Downloading calendar data from: %s", self.name, self.url
            )
            self._wait_for_server()
            self._download_data()
            return self._calendar_data is not None

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

        The user name and password will be set into an HTTPBasicAuthHandler an
        an HTTPDigestAuthHandler.  Both are attached to a new urlopener, so
        that HTTP Basic Auth and HTTP Digest Auth will be supported when
        opening the URL.

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
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.url, user_name, password)
            basic_auth_handler = HTTPBasicAuthHandler(passman)
            digest_auth_handler = HTTPDigestAuthHandler(passman)
            self._opener = build_opener(
                digest_auth_handler, basic_auth_handler
            )

        additional_headers = []
        if user_agent != "":
            additional_headers.append(("User-agent", user_agent))
        if accept_header != "":
            additional_headers.append(("Accept", accept_header))
        if len(additional_headers) > 0:
            if self._opener is None:
                self._opener = build_opener()
            self._opener.addheaders = additional_headers

    def set_timeout(self, connection_timeout: float):
        """Set the connection timeout.

        :param connection_timeout: The timeout value in seconds.
        :type connection_timeout: float
        """
        self.connection_timeout = connection_timeout

    def _wait_for_server(self):
        """Sleep for self._sleep_time to reduce server load."""
        time.sleep(self._sleep_time)

    def _decode_data(self, conn):
        if (
            "Content-Encoding" in conn.headers
            and conn.headers["Content-Encoding"] == "gzip"
        ):
            reader = GzipFile(fileobj=conn)
        else:
            reader = conn
        try:
            return self._decode_stream(reader.read()).replace("\0", "")
        except zlib.error:
            self.logger.error(
                "%s: Failed to uncompress gzip data from url(%s): zlib",
                self.name,
                self.url,
            )
        except BadGzipFile as gzip_error:
            self.logger.error(
                "%s: Failed to uncompress gzip data from url(%s): %s",
                self.name,
                self.url,
                gzip_error.strerror,
            )
        return None

    def _decode_stream(self, strm):
        for encoding in "utf-8-sig", "utf-8", "utf-16":
            try:
                return strm.decode(encoding)
            except UnicodeDecodeError:
                continue
        return None

    def _download_data(self):
        """Download the calendar data."""
        try:
            with CalendarData.opener_lock:
                if self._opener is not None:
                    install_opener(self._opener)
                with urlopen(
                    self._make_url(), timeout=self.connection_timeout
                ) as conn:
                    self._calendar_data = self._decode_data(conn)
        except HTTPError as http_error:
            self.logger.error(
                "%s: Failed to open url(%s): %s",
                self.name,
                self.url,
                http_error.reason,
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

    def _make_url(self):
        now = hanow()
        return self.url.replace("{year}", f"{now.year:04}").replace(
            "{month}", f"{now.month:02}"
        )
