"""Provide GetParser class."""

from __future__ import annotations

from .icalendarparser import ICalendarParser
from .parsers.parser_rie import ParserRIE


class GetParser:  # pylint: disable=R0903
    """Return an instance of the requested parser.

    NOTE: ParserICS is imported lazily to avoid importing the optional `ics`
    dependency at Home Assistant startup.
    """

    @staticmethod
    def get_parser(parser: str, *args) -> ICalendarParser | None:
        """Get an instance of the requested parser."""
        if parser == "rie":
            return ParserRIE(*args)

        if parser == "ics":
            # Lazy import to prevent startup crash if `ics`/`tatsu` combo is broken
            from .parsers.parser_ics import ParserICS  # pylint: disable=import-outside-toplevel

            return ParserICS(*args)

        return None
