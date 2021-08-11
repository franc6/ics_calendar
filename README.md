# ics_calendar
Provides an ICS (icalendar) calendar platform for Home Assistant

> **NOTE**: This calendar platform is intended for use with simple hosting of ICS files.  If your server supports CalDAV, please use the caldav platform instead.  This one might work, but probably not well.

[![License](https://img.shields.io/github/license/franc6/ics_calendar.svg?style=for-the-badge)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Installation
You can install this through [HACS](https://github.com/custom-components/hacs) by adding https://github.com/franc6/ics_calendar as a custom repository.

Otherwise, you can install it manually.

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ics.
4. Download all the files from the custom_components/ics_calendar/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Inside the new directory, run 'pip install -r requirements.txt'
7. Restart Home Assistant
8. Add platform: ics to your HA's calendar configuration.

Using your HA configuration directory (folder) as a starting point you should now also have this:
```
custom_components/ics_calendar/__init__.py
custom_components/ics_calendar/manifest.json
custom_components/ics_calendar/calendar.py
custom_components/ics_calendar/icalendarparser.py
custom_components/ics_calendar/parsers/__init__.py
custom_components/ics_calendar/parsers/parser_ics.py
custom_components/ics_calendar/parsers/parser_icalevents.py
```

## Authentication
This calendar platform supports HTTP Basic Auth and HTTP Digest Auth.  It does
not support more advanced authentication methods.

## Example configuration.yaml
```yaml
calendar:
- platform: ics_calendar
  calendars:
      - name: "Name of calendar"
        url: "https://url.to/calendar.ics"
      - name: "Name of another calendar"
        url: "https://url.to/other_calendar.ics"
        includeAllDay: True
      - name: "Name of a calendar that requires authentication"
        url: "https://url.to/auth/calendar.ics"
        includeAllDay: True
        username: True
        password: !secret auth_calendar
```

## Configuration options
Key | Type | Required | Description
-- | -- | -- | --
`calendars` | `list` | `True` | The list of remote calendars to check

### Configuration options for `calendar` list
Key | Type | Required | Description
-- | -- | -- | --
`name` | `string` | `True` | A name for the calendar
`url` | `string` | `True` | The URL of the remote calendar
`includeAllDay` | `boolean` | `False` | Set to True if all day events should be included
`parser` | `string` | `False` | 'icalevents' or 'ics' Choose 'ics' if you encounter parsing errors, defaults to "icalevents" if not present
`username` | `string` | `False` | If the calendar requires authentication, this specifies the user name
`password` | `string` | `False` | If the calendar requires authentication, this specifies the password

## Parsers
ics_calendar uses one of two parsers for generating events from calendars.
These parsers are written and maintained by third parties, not by me.  Each
comes with its own sets of problems.

Version 1.x used "ics" which does not handle recurring events, and has a few
other problems (see issues #6, #8, and #18).  The "ics" parser is also very
strict, and will frequently give parsing errors for files which do not conform
to RFC 5545.  Some of the most popular calendaring programs produce files that
do not conform to the RFC.  The "ics" parser also tends to require more memory
and processing power.  Several users have noted that it's unusuable for HA
systems running on Raspberry pi computers.

The Version 2.0.0 betas used "icalevents" which is a little more forgiving, but
has a few problems with recurring event rules.  All-day events which repeat
until a specific date and time are a particular issue (all-day events which
repeat until a specific date are just fine).

As a general rule, I recommend sticking with the "icalevents" parser, which is
the default.  If you see parsing errors, you can try switching to "ics" for the
calendar with the parsing errors.

[![Buy me some pizza](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/qpunYPZx5)
