"""Support for ICS Calendar."""
from datetime import date, datetime, timedelta

from icalendar import Calendar
import recurring_ical_events as rie
from ..icalendarparser import ICalendarParser


class parser_rie(ICalendarParser):
    oneday = timedelta(days=1)
    oneday2 = timedelta(hours=23, minutes=59, seconds=59)

    @staticmethod
    def get_event_list(content: str, start, end, include_all_day: bool):
        event_list = []

        calendar = Calendar.from_ical(content)

        if calendar is not None:
            for event in rie.of(calendar).between(start, end):
                start, end, all_day = parser_rie.is_all_day(event)

                if all_day and not include_all_day:
                    continue

                uid = None
                if event.get("UID"):
                    uid = event.get("UID")

                data = {
                    "uid": uid,
                    "summary": event.get("SUMMARY"),
                    "start": start,
                    "end": end,
                    "location": event.get("LOCATION"),
                    "description": event.get("DESCRIPTION"),
                    "all_day": all_day,
                }
                # Note that we return a formatted date for start and end here,
                # but a different format for get_current_event!
                event_list.append(data)

        return event_list

    @staticmethod
    def get_current_event(
        content: str, include_all_day: bool, now: datetime, days: int
    ):
        calendar = Calendar.from_ical(content)

        if calendar is None:
            return None

        temp_event = None
        end = now + timedelta(days=days)
        for event in rie.of(calendar).between(now, end):
            start, end, all_day = parser_rie.is_all_day(event)

            if all_day and not include_all_day:
                continue

            if temp_event is None:
                temp_event = event
                temp_start = start
                temp_end = end
                temp_all_day = all_day
            elif temp_end > end:
                temp_event = event
                temp_start = start
                temp_end = end
                temp_all_day = all_day

        if temp_event is None:
            return None

        return {
            "summary": temp_event.get("SUMMARY"),
            "start": temp_start,
            "end": temp_end,
            "location": temp_event.get("LOCATION"),
            "description": temp_event.get("DESCRIPTION"),
            "all_day": temp_all_day,
        }

    @staticmethod
    def get_date(dt):
        if type(dt) is date:
            dt = datetime.combine(dt, datetime.min.time())
        return dt.astimezone()

    @staticmethod
    def is_all_day(event):
        start = parser_rie.get_date(event.get("DTSTART").dt)
        end = parser_rie.get_date(event.get("DTEND").dt)
        all_day = False
        diff = event.get("DURATION")
        if diff is not None:
            diff = diff.dt
        else:
            diff = end - start
        if (diff == parser_rie.oneday or diff == parser_rie.oneday2) and (
            start.hour == 0 and start.minute == 0 and start.second == 0
        ):
            all_day = True

        return start, end, all_day
