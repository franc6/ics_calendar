from homeassistant.util.dt import now as hanow
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.request import (
    HTTPPasswordMgrWithDefaultRealm,
    HTTPBasicAuthHandler,
    HTTPDigestAuthHandler,
    build_opener,
    install_opener,
    urlopen,
)


class CalendarData:
    def __init__(self, logger, name, url, min_update_time):
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
                    self._calendar_data = conn.read().decode().replace("\0", "")
            except HTTPError as http_error:
                self.logger.error(
                    f"{self.name}: Failed to open url: {http_error.reason}"
                )
            except ContentTooShortError as content_too_short_error:
                self.logger.error(
                    f"{self.name}: Could not download calendar"
                    f" data: {content_too_short_error.reason}"
                )
            except URLError as url_error:
                self.logger.error(
                    f"{self.name}: Failed to open url: {url_error.reason}"
                )
            except:
                self.logger.error(f"{self.name}: Failed to open url!", exc_info=True)
        return

    def get(self):
        self._download_calendar()
        return self._calendar_data

    def setUserNameAndPassword(self, userName, password):
        passman = HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.url, userName, password)
        basic_auth_handler = HTTPBasicAuthHandler(passman)
        digest_auth_handler = HTTPDigestAuthHandler(passman)
        opener = build_opener(digest_auth_handler, basic_auth_handler)
        install_opener(opener)
