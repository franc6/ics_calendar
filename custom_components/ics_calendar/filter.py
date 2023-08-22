"""Provide Filter class."""
import re
from ast import literal_eval
from typing import List, Optional, Pattern

from homeassistant.components.calendar import CalendarEvent


class Filter:
    """Filter class.

    The Filter class is used to filter events according to the exclude and
    include rules.
    """

    def __init__(self, exclude: str, include: str):
        """Construct Filter class.

        :param exclude: The exclude rules
        :type exclude: str
        :param include: The include rules
        :type include: str
        """
        self._exclude = Filter.set_rules(exclude)
        self._include = Filter.set_rules(include)

    @staticmethod
    def set_rules(rules: str) -> List[Pattern]:
        """Set the given rules into an array which is returned.

        :param rules: The rules to set
        :type rules: str
        :return: An array of regular expressions
        :rtype: List[Pattern]
        """
        arr = []
        if rules != "":
            for rule in literal_eval(rules):
                if rule.startswith("/"):
                    re_flags = re.NOFLAG
                    [expr, flags] = rule[1:].split("/")
                    for flag in flags:
                        match flag:
                            case "i":
                                re_flags |= re.IGNORECASE
                            case "m":
                                re_flags |= re.MULTILINE
                            case "s":
                                re_flags |= re.DOTALL
                    arr.append(re.compile(expr, re_flags))
                else:
                    arr.append(re.compile(rule, re.IGNORECASE))
        return arr

    def _is_match(
        self, summary: str, description: Optional[str], regexes: List[Pattern]
    ) -> bool:
        """Indicate if the event matches the given list of regular expressions.

        :param summary: The event summary to examine
        :type summary: str
        :param description: The event description summary to examine
        :type description: Optional[str]
        :param regexes: The regular expressions to match against
        :type regexes: List[]
        :return: True if the event matches the exclude filter
        :rtype: bool
        """
        for regex in regexes:
            if regex.search(summary) or (
                description and regex.search(description)
            ):
                return True

        return False

    def _is_excluded(self, summary: str, description: Optional[str]) -> bool:
        """Indicate if the event should be excluded.

        :param summary: The event summary to examine
        :type summary: str
        :param description: The event description summary to examine
        :type description: Optional[str]
        :return: True if the event matches the exclude filter
        :rtype: bool
        """
        return self._is_match(summary, description, self._exclude)

    def _is_included(self, summary: str, description: Optional[str]) -> bool:
        """Indicate if the event should be included.

        :param summary: The event summary to examine
        :type summary: str
        :param description: The event description summary to examine
        :type description: Optional[str]
        :return: True if the event matches the include filter
        :rtype: bool
        """
        return self._is_match(summary, description, self._include)

    def filter(self, summary: str, description: Optional[str]) -> bool:
        """Check if the event should be included or not.

        :param summary: The event summary to examine
        :type summary: str
        :param description: The event description summary to examine
        :type description: Optional[str]
        :return: true if the event should be included, otherwise false
        :rtype: bool
        """
        add_event = not self._is_excluded(summary, description)
        if not add_event:
            add_event = self._is_included(summary, description)
        return add_event

    def filter_event(self, event: CalendarEvent) -> bool:
        """Check if the event should be included or not.

        :param event: The event to examine
        :type event: CalendarEvent
        :return: true if the event should be included, otherwise false
        :rtype: bool
        """
        return self.filter(event.summary, event.description)
