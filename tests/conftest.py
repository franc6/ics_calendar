import pytest
import sys
from custom_components.ics_calendar.icalendarparser import ICalendarParser

@pytest.fixture
def ics_parser():
    return ICalendarParser.get_instance('ics')

@pytest.fixture
def icalevents_parser():
    return ICalendarParser.get_instance('icalevents')

@pytest.fixture()
def calendar_data(fileName):
    return open("tests/" + fileName).read().replace('\0', '')
