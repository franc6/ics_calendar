# ics_calendar
Provides a calendar component for Home Assistant via ICS

##To configure
```yaml
calendar:
- platform: ics
  calendars:
      - name: "Name of calendar"
        url: "https://url.to/calendar.ics"
      - name: "Name of another calendar"
        url: "https://url.to/other_calendar.ics"
        includeAllDay: true
```

##Install
	TODO
