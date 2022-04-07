"""Fixtures and helpers for tests."""
import json

import pytest
from dateutil import parser as dtparser

from custom_components.ics_calendar.icalendarparser import ICalendarParser


def datetime_hook(pairs):
    """Parse datetime values from JSON."""
    _dict = {}
    for key, value in pairs:
        if isinstance(value, str):
            try:
                _dict[key] = dtparser.parse(value)
            except ValueError:
                _dict[key] = value
        else:
            _dict[key] = value
    return _dict


@pytest.fixture
def rie_parser():
    """Fixture for rie parser."""
    return ICalendarParser.get_instance("rie")


@pytest.fixture
def ics_parser():
    """Fixture for ics parser."""
    return ICalendarParser.get_instance("ics")


@pytest.fixture
def parser(which_parser, request):
    """Fixture for getting a parser.

    :param which_parser identifies the parser fixture, ParserRIE or ParserICS
    :type which_parser str
    :param request the request for the fixture
    :returns an instance of the requested parser
    :rtype ICalendarParser
    """
    return request.getfixturevalue(which_parser)


@pytest.fixture()
def calendar_data(file_name):
    """Return contents of a file with embedded NULL removed.

    :param fileName The name of the file
    :type str
    :returns the data
    :rtype str
    """
    with open(f"tests/{file_name}") as file_handle:
        return file_handle.read().replace("\0", "")


@pytest.fixture()
def expected_data(file_name):
    """Return content of tests/{fileName}.expected.json.

    :param fileName: The base name of the file
    :type fileName: str
    """
    with open(f"tests/{file_name}.expected.json") as file_handle:
        return json.loads(file_handle.read(), object_pairs_hook=datetime_hook)


@pytest.helpers.register
def assert_event_list_size(expected, event_list):
    """Assert event_list is not None and has the expected number of events.

    :param expected: The number of events that should be in event_list
    :type expected: int
    :param event_list: The array of events to check
    :type event_list: array
    """
    assert event_list is not None
    assert expected == len(event_list)


@pytest.helpers.register
def compare_event_list(expected, actual):
    """Assert that each item in expected matches the item in actual.

    :param expected: The data to expect
    :type expected: dict
    :param actual: The data to check
    :type actual: dict
    """
    for expected_part, actual_part in zip(expected, actual):
        pytest.helpers.compare_event(expected_part, actual_part)


@pytest.helpers.register
def compare_event(expected, actual):
    """Assert actual event matches expected event.

    :param expected: The event to expect
    :type expected: dict
    :param actual: The event to check
    :type actual: dict
    """
    for key in expected.keys():
        assert expected is not None
        assert actual is not None
        assert expected[key] == actual[key]
