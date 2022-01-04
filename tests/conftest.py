import pytest
import json
from dateutil import parser as dtparser

from custom_components.ics_calendar.icalendarparser import ICalendarParser


def datetime_hook(pairs):
    dict = {}
    for key, value in pairs:
        if isinstance(value, str):
            try:
                dict[key] = dtparser.parse(value)
            except ValueError:
                dict[key] = value
        else:
            dict[key] = value
    return dict


@pytest.fixture
def rie_parser():
    return ICalendarParser.get_instance("rie")


@pytest.fixture
def ics_parser():
    return ICalendarParser.get_instance("ics")


@pytest.fixture
def icalevents_parser():
    return ICalendarParser.get_instance("icalevents")


@pytest.fixture
def parser(which_parser, request):
    return request.getfixturevalue(which_parser)


@pytest.fixture()
def calendar_data(fileName):
    with open(f"tests/{fileName}") as f:
        return f.read().replace("\0", "")


@pytest.fixture()
def expected_data(fileName):
    with open(f"tests/{fileName}.expected.json") as f:
        return json.loads(f.read(), object_pairs_hook=datetime_hook)


@pytest.helpers.register
def assert_event_list_size(expected, event_list):
    assert event_list is not None
    assert expected == len(event_list)


@pytest.helpers.register
def compare_event_list(expected, actual):
    for e, a in zip(expected, actual):
        pytest.helpers.compare_event(e, a)


@pytest.helpers.register
def compare_event(expected, actual):
    for key in expected.keys():
        assert expected[key] == actual[key]
