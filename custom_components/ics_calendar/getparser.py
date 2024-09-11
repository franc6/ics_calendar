"""Provide GetParser class."""

from .icalendarparser import ICalendarParser
from .parsers.parser_ics import ParserICS
from .parsers.parser_rie import ParserRIE


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
            return ParserICS(*args)

        return None
