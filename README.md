# ics_calendar
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![ics_calendar](https://img.shields.io/github/v/release/franc6/ics_calendar.svg?1)](https://github.com/franc6/ics_calendar)
[![Coverage](https://codecov.io/gh/franc6/ics_calendar/branch/releases/graph/badge.svg)](https://app.codecov.io/gh/franc6/ics_calendar/branch/releases)
![Maintained:yes](https://img.shields.io/maintenance/yes/2025.svg)
[![License](https://img.shields.io/github/license/franc6/ics_calendar.svg)](LICENSE)

Provides a component for ICS (icalendar) calendars for Home Assistant

> **NOTE**: This component is intended for use with simple hosting of ICS files.  If your server supports CalDAV, please use the caldav calendar platform instead.  This one might work, but probably not well.

> **NOTE**: Because https://www.home-assistant.io/integrations/remote_calendar now exists, this project will eventually close.  I may or may not add some of the features that project is missing.  This will stick around for at least a couple more releases, since I know some people will be unable to use the Remote Calendar integration due to its current limitations.  If anyone thinks it's worth keeping this project going even after Remote Calendar gets close to feature parity, I'm willing to transfer ownership.  I just have no desire to work on a project that's duplicating something else that exists.

## Installation
You can install this through [HACS](https://github.com/custom-components/hacs).

### Warning when installing in HA in a container
A number of users have reported problems when running HA in a container.  If you see any of these messages in your log,
```
- Setup failed for custom integration 'ics_calendar': Requirements for ics_calendar not found
- ModuleNotFoundError: No module named 'ics'
- ModuleNotFoundError: No module named 'recurring-icalendar-events'
- ImportError: Exception importing custom_components.ics_calendar.calendar
- AttributeError: module 'icalendar' has no attribute 'InvalidCalendar'
```

Then your problem stems from a dependency installation issue.  This problem is supposed to be resolved in HA 2025.1, but it's possible that you still have trouble, because of one or more of the following:

1. you are running in an unsupported container environment
2. you have made custom modifications to the container
3. you have made custom modifications to the container in order to resolve an earlier dependency problem, for this integration or another

If you encounter a dependency installation problem, please see https://github.com/home-assistant/core/issues/127966 and https://github.com/home-assistant/core/pull/125808 which explain the problem in more detail, and the fix that was applied.  If those do not help you resolve the dependency problem, please note that the author will be unable to help.  Please do not open an issue on GitHub for this problem.  It's not a bug in ics_calendar, and it cannot be resolved by changing ics_calendar.  You can find the full list of runtime dependencies and versions in the [manifest.json](custom_components/ics_calendar/manifest.json) in the "requirements" value.

### Manual installation

The following procedure should work, but is **strongly** discouraged.

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ics_calendar.
4. Download all the files from the custom_components/ics_calendar/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

Using your HA configuration directory (folder) as a starting point you should now also have this:
```
custom_components/ics_calendar/__init__.py
custom_components/ics_calendar/calendar.py
custom_components/ics_calendar/calendardata.py
custom_components/ics_calendar/config_flow.py
custom_components/ics_calendar/const.py
custom_components/ics_calendar/filter.py
custom_components/ics_calendar/getparser.py
custom_components/ics_calendar/icalendarparser.py
custom_components/ics_calendar/manifest.json
custom_components/ics_calendar/parsers/__init__.py
custom_components/ics_calendar/parsers/parser_ics.py
custom_components/ics_calendar/parsers/parser_rie.py
custom_components/ics_calendar/strings.json
custom_components/ics_calendar/translations/en.json
custom_components/ics_calendar/utility.py
```

## Authentication
This component supports HTTP Basic Auth and HTTP Digest Auth.  It does not support more advanced authentication methods.

## Configuration
Configuration is done via UI now.  Go to https://my.home-assistant.io/redirect/integrations/ and click "Add Integration" to add ICS Calendar.  You'll want to do this for each calendar for this integration.

Please note that if you previously used configuration.yaml, you must remove those entries after updating to a version that supports UI configuration.

## Example configuration.yaml
```yaml
ics_calendar:
  calendars:
    - name: "Name of calendar"
      url: "https://url.to/calendar.ics"
    - name: "Name of another calendar"
      url: "https://url.to/other_calendar.ics"
      include_all_day: True
    - name: "Name of a calendar that requires authentication"
      url: "https://url.to/auth/calendar.ics"
      include_all_day: True
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
`url` | `string` | `True` | The URL of the calendar (https and file URI schemes are supported)
`accept_header` | `string` | An accept header for servers that are misconfigured, default is not set
`connection_timeout` | `float` | `None` | Sets a timeout in seconds for the connection to download the calendar.  Use this if you have frequent connection issues with a calendar
`days` | `positive integer` | `False` | The number of days to look ahead (only affects the attributes of the calendar entity), default is 1
`download_interval` | `positive integer` | `False` | The time between downloading new calendar data, in minutes, default is 15
`exclude` | `string` | `False` | Allows for filtering of events, see below
`include` | `string` | `False` | Allows for filtering of events, see below
`include_all_day` | `boolean` | `False` | Set to True if all day events should be included
`offset_hours` | `int` | `False` | A number of hours (positive or negative) to offset times by, see below
`parser` | `string` | `False` | 'rie' or 'ics', defaults to 'rie' if not present
`prefix` | `string` | `False` | Specify a string to prefix every event summary with, see below
`username` | `string` | `False` | If the calendar requires authentication, this specifies the user name
`password` | `string` | `False` | If the calendar requires authentication, this specifies the password
`user_agent` | `string` | `False` | Allows setting the User-agent header.  Only specify this if your server rejects the normal python user-agent string.  You must set the entire and exact user agent string here.

#### Download Interval
The download interval should be a multiple of 15 at this time.  This is so downloads coincide with Home Assistant's update interval for the calendar entities. Setting a value smaller than 15 will increase both CPU and memory usage.  Higher values will reduce CPU usage.  The default of 15 is to keep the same behavior with regards to downloads as in the past.

Home Assistant does two types of queries. One is the 15 minute calendar entity update, the other is a query every time the `calendar.list_events` service is called. This interval limit applies to both.
On top of that there can be globally only one download in progress for all calendars. This might be an issue with lots of calendars and slow server response.

#### Offset Hours
This feature is to aid with calendars that present incorrect times.  If your calendar has an incorrect time, e.g. it lists your local time, but indicates that it's the time in UTC, this can be used to correct for your local time.  This affects all events, except all day events.  All day events do not include time information, and so the offset will not be applied.  Use a positive number to add hours to the time, and a negative number to subtract hours from the time.

#### Prefix
This feature prefixes each summary with the given string.  You might want to have some whitespace between the prefix and original event summary.  You must include whatever whitespace you want in your configuration, so be sure to quote the string.  E.g.:

```yaml
ics_calendar:
  calendars:
    - name: "Name of calendar"
      url: "https://url.to/calendar.ics"
      prefix: 'ICS Prefix '
```

## Parsers
ics_calendar uses one of two parsers for generating events from calendars.  These parsers are written and maintained by third parties, not by me.  Each comes with its own sets of problems.

Version 1.x used "ics" which does not handle recurring events, and has a few other problems (see issues #6, #8, and #18).  The "ics" parser is also very strict, and will frequently give parsing errors for files which do not conform to RFC 5545.  Some of the most popular calendaring programs produce files that do not conform to the RFC.  The "ics" parser also tends to require more memory and processing power.  Several users have noted that it's unusuable for HA systems running on Raspberry pi computers.

The Version 2.0.0 betas used "icalevents" which is a little more forgiving, but has a few problems with recurring event rules.  All-day events which repeat until a specific date and time are a particular issue (all-day events which repeat until a specific date are just fine).

In Version 2.5 and later, a new parser, "rie" is the default.  Like "icalevents", it's based on the "icalendar" library.  This parser appears to fix both issues #8 and #36, which are problematic for "icalevents".

Starting with version 2.7, "icalevents" is no longer available.  If you have specified icalevents as the parser, please change it to rie or ics.

As a general rule, I recommend sticking with the "rie" parser, which is the default.  If you see parsing errors, you can try switching to "ics" for the calendar with the parsing errors.

## Filters
The new exclude and include options allow for filtering events in the calendar.  This is a string representation of an array of strings or regular expressions.  They are used as follows:

The exclude filters are applied first, searching in the summary and description only.  If an event is excluded by the exclude filters, the include filters will be checked to determine if the event should be included anyway.

Regular expressions can be used, by surrounding the string with slashes (/).  You can also specify case insensitivity, multi-line match, and dotall matches by appending i, m, or s (respectively) after the ending slash.  If you don't understand what that means, you probably just want to stick with plain string matching.  For example, if you specify "['/^test/i']" as your exclude filter, then any event whose summary or description starts with "test", "Test", "TEST", etc. will be excluded.

For plain string matching, the string will be searched for in a case insensitive manner.  For example, if you specify "['test']" for your exclude filter, any event whose summary or description contains "test", "Test", "TEST", etc. will be excluded.  Since this is not a whole-word match, this means if the summary or description contains "testing" or "stesting", the event will be excluded.

You can also include multiple entries for exclude or include.

> **NOTE**: If you want to include only events that include a specific string, you **must** use an exclude filter that excludes everything in addition to your include filter.  E.g. "['/.*/']"

### Examples
```yaml
ics_calendar:
  calendars:
    - name: "Name of calendar"
      url: "https://url.to/calendar.ics"
      exclude: "['test', '/^regex$/']"
      include: "['keepme']"
```

This example will exclude any event whose summary or description includes "test" in a case insensitive manner, or if the summary or description is "regex".  However, if the summary or description includes "keepme" (case insensitive), the event will be included anyway.

## URL Templates
If your ICS url requires specifying the current year and/or month, you can now use templates to specify the current year and month.  E.g. if you set your url to:
```yaml
url: "https://www.a-url?year={year}&month={month}"
```

The "{year}" part will be replaced with the current 4 digit year, and the "{month}" part will be replaced with the current 2 digit month.  So in February 2023, the URL will be "https://www.a-url?year=2023&month=02", in November 2024, the URL will be "https://www.a-url?year=2024&month=11".

You can also specify positive and negative offsets for the year and month templates. E.g. if you set your url to:
```yaml
url: "https://www.a-url?year={year+1}&month={month-3}"
```

The "{year+1}" part will be replaced with the next 4 digit year, and the "{month-3}" part will be replaced with the 2 digit month of three months ago.  So in February 2023, the URL will be "https://www.a-url?year=2023&month=11", in November 2024, the URL will be "https://www.a-url?year=2025&month=8".

## Development environment setup

You should have uv installed.  Then run the following commands:

```shell
$ uv sync --dev --extra tests
$ source ./.venv/bin/activate # for CSH shells
$ . ./.venv/bin/activate # for most other shells
```

[![Buy me some pizza](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/qpunYPZx5)
