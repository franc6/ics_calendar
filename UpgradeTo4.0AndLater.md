This file covers upgrading from ics_calendar version 3.x or earlier to version 4.0.x.  Please read it carefully and make the necessary configuration changes, or you may experience problems.  If you are installing version 4.0.x and have not used ics_calendar before, you don't need to read this document.  Just follow the configuration instructions in [README.md](https://github.com/franc6/ics_calendar/blob/releases/README.md).

Version 4.0.0 includes some breaking changes that allow for a future version that is configurable via the UI, and supports unique_id.  This future version will fix issues 88 and 89.  They are not fixed in 4.0.0.

Your existing configuration from version 3.2.0 or earlier will **not** work with version 4.0.0 and later.

The basic change is to move the ics_calendar configuration to a top-level item, instead of being a platform entry under calendar.  See the examples below.

## Steps to upgrade
1. Install new version of ics_calendar via HACS or manually.  **Do NOT restart Home Assistant yet!**
2. Update YAML configuration, using the examples below for reference.
3. Restart Home Assistant.

## Examples

### Example in configuration.yaml with only ics_calendar calendars

Current configuration.yaml

```yaml
calendar:
  - platform: ics_calendar
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

New configuration.yaml

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

### Example in configuration.yaml with caldav and ics_calendar calendars:

Current configuration.yaml

```yaml
calendar:
  - platform: caldav
    username: user
    password: !secret caldav_password
    url: https://example.com/.well-known/caldav
  - platform: ics_calendar
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

New configuration.yaml

```yaml
calendar:
  - platform: caldav
    username: user
    password: !secret caldav_password
    url: https://example.com/.well-known/caldav

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

### Example in external yaml file with only ics_calendar calendars:

Current configuration.yaml

```yaml
calendar: !include calendars.yaml
```

Current calendars.yaml

```yaml
- platform: ics_calendar
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

New configuration.yaml

```yaml
ics_calendar: !include calendars.yaml
```

New calendars.yaml
```yaml
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

### Example in external yaml file, with caldav and ics_calendar calendars:

Current configuration.yaml

```yaml
calendar: !include calendars.yaml
```

Current calendars.yaml

```yaml
- platform: caldav
  username: user
  password: !secret caldav_password
  url: https://example.com/.well-known/caldav
- platform: ics_calendar
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

New configuration.yaml

```yaml
calendar: !include calendars.yaml
ics_calendar: !include ics_calendars.yaml
```

New calendars.yaml

```yaml
- platform: caldav
  username: user
  password: !secret caldav_password
  url: https://example.com/.well-known/caldav
```

New ics_calendars.yaml

```yaml
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