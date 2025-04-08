"""Provide ParserEvent class."""

import dataclasses

from homeassistant.components.calendar import CalendarEvent


@dataclasses.dataclass
class ParserEvent(CalendarEvent):
    """Class to represent CalendarEvent without validation."""

    def validate(self) -> None:
        """Invoke __post_init__ from CalendarEvent."""
        return super().__post_init__()

    def __post_init__(self) -> None:
        """Don't do validation steps for this class."""
        # This is necessary to prevent problems when creating events that don't
        # have a summary. We'll add a summary after the event is created, not
        # before, to reduce code repitition.
