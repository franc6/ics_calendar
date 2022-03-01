"""Support for ICS Calendar."""
import re
from arrow import Arrow, get as arrowget
from datetime import datetime, timedelta
from ics import Calendar
from ..icalendarparser import ICalendarParser


class parser_ics(ICalendarParser):
    re_method = re.compile("^METHOD:.*$", flags=re.MULTILINE)

    @staticmethod
    def get_event_list(content: str, start, end, include_all_day: bool):
        event_list = []

        calendar = Calendar(re.sub(parser_ics.re_method, "", content))

        if calendar is not None:
            # ics 0.8 takes datetime not Arrow objects
            # ar_start = start
            # ar_end = end
            ar_start = arrowget(start)
            ar_end = arrowget(end)

            for event in calendar.timeline.included(ar_start, ar_end):
                if event.all_day and not include_all_day:
                    continue
                uid = None
                summary = ""
                if hasattr(event, "uid"):
                    uid = event.uid
                # ics 0.8 uses 'summary' reliably, older versions use 'name'
                if hasattr(event, "summary"):
                    summary = event.summary
                elif hasattr(event, "name"):
                    summary = event.name
                # print("event: ")
                # print(vars(event))
                data = {
                    "uid": uid,
                    "summary": summary,
                    "start": parser_ics.get_date(event.begin, event.all_day),
                    "end": parser_ics.get_date(event.end, event.all_day),
                    "location": event.location,
                    "description": event.description,
                    "all_day": event.all_day,
                }
                # Note that we return a formatted date for start and end here,
                # but a different format for get_current_event!
                event_list.append(data)

        return event_list

    @staticmethod
    def get_current_event(
        content: str, include_all_day: bool, now: datetime, days: int
    ):
        calendar = Calendar(content)

        if calendar is None:
            return None

        temp_event = None
        end = now + timedelta(days=days)
        for event in calendar.timeline.included(arrowget(now), arrowget(end)):
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
            "start": parser_ics.get_date(temp_event.begin, temp_event.all_day),
            "end": parser_ics.get_date(temp_event.end, temp_event.all_day),
            "location": temp_event.location,
            "description": temp_event.description,
            "all_day": temp_event.all_day,
        }

    @staticmethod
    def get_date(arw, is_all_day):
        if type(arw) == Arrow:
            if is_all_day:
                arw = arw.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo="local"
                )
            return arw.datetime
        else:
            if arw.tzinfo is None or arw.tzinfo.utcoffset(arw) is None or is_all_day:
                arw = arw.astimezone()

        return arw
