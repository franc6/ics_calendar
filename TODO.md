# Updates for v5.X

## Unit tests
- [ ] Add unit tests for UI configuration methods
- [ ] Add unit tests for setup entry points in ics_calendar/__init__.py

## General
- [X] Figure out how to get entries named something other than "ICS Calendar" when looking at separate entries in Setup (5.0.4)

## UI Config
- [ ] Revamp UI config, especially for URLs (see #133, #116, #169)

# Updates for v6.0.0

## Remove YAML config support
- [ ] Remove methods and unit tests

## UI Config
- [ ] Break UI config into config_flow and options_flow
- [ ] Allow reconfigure of options
    - Name & unique ID should be kept, everything else can be reconfigured
    - Users that want to change the name can use HA's entity configuration to do that
