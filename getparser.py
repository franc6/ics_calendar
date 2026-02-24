"""Provide GetParser class."""

import logging

from .icalendarparser import ICalendarParser
from .parsers.parser_rie import ParserRIE

_LOGGER = logging.getLogger(__name__)

try:
    from .parsers.parser_ics import ParserICS

    _ICS_IMPORT_ERROR = None
except ImportError as err:
    _ICS_IMPORT_ERROR = err
    _LOGGER.error(
        "ics parser failed to load: %s. "
        "Check that tatsu<5.8.0 is installed, or switch to the "
        "'rie' parser in your calendar configuration.",
        err,
    )


class GetParser:  # pylint: disable=R0903
    """Provide get_parser to return an instance of ICalendarParser.

    The class provides a static method , get_instace, to get a parser instance.
    The non static methods allow this class to act as an "interface" for the
    parser classes.
    """

    @staticmethod
    def get_parser(parser: str, *args) -> ICalendarParser | None:
        """Get an instance of the requested parser."""
        # parser_cls = ICalendarParser.get_class(parser)
        # if parser_cls is not None:
        # return parser_cls(*args)
        if parser == "rie":
            return ParserRIE(*args)
        if parser == "ics":
            if _ICS_IMPORT_ERROR is not None:
                raise ImportError(
                    f"ics parser is unavailable: {_ICS_IMPORT_ERROR}. "
                    "Check that tatsu<5.8.0 is installed, or switch to the "
                    "'rie' parser in your calendar configuration."
                ) from _ICS_IMPORT_ERROR
            return ParserICS(*args)

        return None
