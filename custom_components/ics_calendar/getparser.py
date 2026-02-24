"""Provide GetParser class."""

from .icalendarparser import ICalendarParser


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
            from .parsers.parser_rie import (  # pylint: disable=C0415
                ParserRIE,
            )

            return ParserRIE(*args)
        if parser == "ics":
            from .parsers.parser_ics import (  # pylint: disable=C0415
                ParserICS,
            )

            return ParserICS(*args)

        return None
