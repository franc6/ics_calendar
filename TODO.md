# Updates for v5.X

## Unit tests
- [ ] Add unit tests for UI configuration methods
- [ ] Add unit tests for setup entry points in ics_calendar/__init__.py

## General
- [X] Figure out how to get entries named something other than "ICS Calendar" when looking at separate entries in Setup (5.0.4)

## UI Config
- [ ] Revamp UI config, especially for URLs (see #133, #116, #169)

## HTTP Changes
- [ ] Fix #166; use homeassistant.helpers.httpx_client.create_async_httpx_client (or get_async_client?) along with httpx_auth to handle HTTP(S) connections.  Need to create a multi-auth capable DigetAuth, too. See https://github.com/Colin-b/httpx_auth/blob/develop/httpx_auth/_authentication.py (class Basic) for an example of doing that.  This means more advanced authentication mechanisms will also be supported!

# Updates for v6.0.0

## Remove YAML config support
- [ ] Remove methods and unit tests

## UI Config
- [ ] Break UI config into config_flow and options_flow
- [ ] Allow reconfigure of options
    - Name & unique ID should be kept, everything else can be reconfigured
    - Users that want to change the name can use HA's entity configuration to do that
