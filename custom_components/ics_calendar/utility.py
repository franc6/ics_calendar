"""Utility methods."""
from datetime import date, datetime


def make_datetime(val):
    """Ensure val is a datetime, not a date."""
    if isinstance(val, date) and not isinstance(val, datetime):
        return datetime.combine(val, datetime.min.time()).astimezone()
    return val


def compare_event_dates(  # pylint: disable=R0913
    now, end2, start2, all_day2, end, start, all_day
) -> bool:
    """Determine if end2 and start2 are newer than end and start."""
    # Make sure we only compare datetime values, not dates with datetimes.
    # Set each date object to a datetime at midnight.
    end = make_datetime(end)
    end2 = make_datetime(end2)
    start = make_datetime(start)
    start2 = make_datetime(start2)

    if all_day2 == all_day:
        if end2 == end:
            return start2 > start
        return end2 > end and start2 >= start

    if now.tzinfo is None:
        now = now.astimezone()

    event2_current = start2 <= now <= end2
    event_current = start <= now <= end

    if event_current and event2_current:
        return all_day

    return start2 >= start or end2 >= end
