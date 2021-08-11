"""Support for ICS Calendar."""
import re
from arrow import get as arrowget, utcnow
from ics import Calendar
from ..icalendarparser import ICalendarParser


class parser_ics(ICalendarParser):
    re_method = re.compile("^METHOD:.*$", flags=re.MULTILINE)

    @staticmethod
    def get_event_list(content: str, start, end, include_all_day: bool):
        event_list = []

        calendar = Calendar(re.sub(parser_ics.re_method, "", content))

        if calendar is not None:
            ar_start = arrowget(start)
            ar_end = arrowget(end)

            for event in calendar.timeline.included(ar_start, ar_end):
                if event.all_day and not include_all_day:
                    continue
                uid = None
                if hasattr(event, "uid"):
                    uid = event.uid
                data = {
                    "uid": uid,
                    "summary": event.name,
                    "start": parser_ics.get_date_formatted(event.begin, event.all_day),
                    "end": parser_ics.get_date_formatted(event.end, event.all_day),
                    "location": event.location,
                    "description": event.description,
                }
                # Note that we return a formatted date for start and end here,
                # but a different format for get_current_event!
                event_list.append(data)

        return event_list

    @staticmethod
    def get_current_event(content: str, include_all_day: bool):
        calendar = Calendar(content)

        if calendar is None:
            return None
        temp_event = None
        for event in calendar.timeline.at(utcnow()):
            if event.all_day and not include_all_day:
                continue
            if temp_event is None:
                temp_event = event
            elif temp_event.end > event.end:
                temp_event = event

        if temp_event is None:
            return None

        return {
            "summary": temp_event.name,
            "start": parser_ics.get_hass_date(temp_event.begin, temp_event.all_day),
            "end": parser_ics.get_hass_date(temp_event.end, temp_event.all_day),
            "location": temp_event.location,
            "description": temp_event.description,
        }

    @staticmethod
    def get_date_formatted(arw, is_all_day):
        """Return the formatted date"""
        # Note that all day events should have a time of 0, and the timezone
        # must be local.  The server probably has the timezone erroneously set
        # to UTC!
        if is_all_day:
            arw = arw.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo="local")
            return arw.format("YYYY-MM-DD")

        return arw.isoformat()

    @staticmethod
    def get_hass_date(arw, is_all_day):
        """Return the wrapped and formatted date"""
        if is_all_day:
            return {"date": parser_ics.get_date_formatted(arw, is_all_day)}
        return {"dateTime": parser_ics.get_date_formatted(arw, is_all_day)}
