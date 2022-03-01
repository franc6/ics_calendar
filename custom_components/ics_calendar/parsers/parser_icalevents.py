"""Support for ICS Calendar."""
from datetime import datetime, timedelta
from icalevents import icalparser
from ..icalendarparser import ICalendarParser


class parser_icalevents(ICalendarParser):
    @staticmethod
    def get_event_list(content: str, start, end, include_all_day: bool):
        event_list = []
        events = icalparser.parse_events(content=content, start=start, end=end)
        if events is not None:
            for event in events:
                if event.all_day and not include_all_day:
                    continue
                uid = None
                if hasattr(event, "uid") and event.uid != -1:
                    uid = event.uid
                data = {
                    "uid": uid,
                    "summary": event.summary,
                    "start": event.start.astimezone(),
                    "end": event.end.astimezone(),
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
        now = now.astimezone()
        end = now + timedelta(days=days)
        events = icalparser.parse_events(content=content, start=now, end=end)
        if events is None or len(events) == 0:
            return None

        temp_event = None
        for event in events:
            if event.all_day and not include_all_day:
                continue
            event.start = event.start.astimezone()
            event.end = event.end.astimezone()

            if (event.end >= now) and (
                temp_event is None or event.start < temp_event.start
            ):
                temp_event = event

        if temp_event is None:
            return None

        return {
            "summary": temp_event.summary,
            "start": temp_event.start,
            "end": temp_event.end,
            "location": temp_event.location,
            "description": temp_event.description,
            "all_day": temp_event.all_day,
        }
