# ics_calendar
Provides an ICS (icalendar) calendar platform for Home Assistant

[![License](https://img.shields.io/github/license/franc6/ics_calendar.svg?style=for-the-badge)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Installation
You can install this through [HACS](https://github.com/custom-components/hacs) by adding https://github.com/franc6/ics_calendar as a custom repository.

Otherwise, you can install it manually.

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ics.
4. Download all the files from the custom_components/ics/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Inside the new directory, run 'pip install -r requirements.txt'
7. Restart Home Assistant
8. Add platform: ics to your HA's calendar configuration.

Using your HA configuration directory (folder) as a starting point you should now also have this:
```
custom_components/ics/__init__.py
custom_components/ics/manifest.json
custom_components/ics/calendar.py
```

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

[![Buy me some pizza](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/qpunYPZx5)
