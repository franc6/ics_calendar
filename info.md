# ics_calendar
Provides an ICS (icalendar) calendar platform for Home Assistant

[![License](https://img.shields.io/github/license/franc6/ics_calendar.svg?style=for-the-badge)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Installation
You can install this through [HACS](https://github.com/custom-components/hacs) by adding https://github.com/franc6/ics_calendar as a custom repository.

Using your HA configuration directory (folder) as a starting point you should now also have this:
```
custom_components/ics/__init__.py
custom_components/ics/manifest.json
custom_components/ics/calendar.py
```

## Authentication
This calendar platform supports HTTP Basic Auth and HTTP Digest Auth.  It does
not support more advanced authentication methods.

## Example configuration.yaml
```yaml
calendar:
- platform: ics
  calendars:
      - name: "Name of calendar"
        url: "https://url.to/calendar.ics"
      - name: "Name of another calendar"
        url: "https://url.to/other_calendar.ics"
        includeAllDay: True
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
`username` | `string` | `False` | If the calendar requires authentication, this specifies the user name
`password` | `string` | `False` | If the calendar requires authentication, this specifies the password

[![Buy me some pizza](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/qpunYPZx5)
