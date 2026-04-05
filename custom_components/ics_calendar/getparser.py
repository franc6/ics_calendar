"""Provide GetParser class."""

from .icalendarparser import ICalendarParser


class GetParser:  # pylint: disable=R0903
    """Provide get_parser_async to return an instance of ICalendarParser.

    The class provides a static method, get_parser_async, to get a parser
    instance.  The non static methods allow this class to act as an "interface"
    for the parser classes.
    """

    @staticmethod
    async def get_parser_async(
        hass, parser: str, *args
    ) -> ICalendarParser | None:
        """Get an instance of the requested parser asynchronously.

        This method loads the parser module in an executor to avoid blocking
        the event loop during timezone data loading.
        """
        if parser == "rie":

            def _load_rie_parser():
                from .parsers.parser_rie import (  # pylint: disable=C0415
                    ParserRIE,
                )

                return ParserRIE(*args)

            return await hass.async_add_executor_job(_load_rie_parser)

        if parser == "ics":

            def _load_ics_parser():
                from .parsers.parser_ics import (  # pylint: disable=C0415
                    ParserICS,
                )

                return ParserICS(*args)

            return await hass.async_add_executor_job(_load_ics_parser)

        return None
