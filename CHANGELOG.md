## 4.2.0 2024/01/15
- Add timeout feature.  Thanks to @iamjackg!
- Fixed #117

## 4.1.0 2023/11/07
- Add feature for #107

## 4.0.1 2023/10/24
- Attempt to give an error message for missing configuration

## 4.0.0 2023/10/17
- Change to be a component, since HA doesn't seem likely to allow UI configuration of the calendar component. :(
### Breaking Change
You must update your YAML configuration with this update.  This integration is no longer a platform for the calendar component.  Instead, it's a component on its own that provides calendars.  Please see [UpgradeTo4.0AndLater.md](https://github.com/franc6/ics_calendar/blob/releases/UpgradeTo4.0AndLater.md) for more information on upgrading.  Please read that carefully before upgrading to this version!

## 3.2.0 2023/09/19
- Added new option, accept_header to allow setting an Accept header for misconfigured servers.
- Updated dependencies

## 3.1.8 2023/08/23
- Fixed #90
- Fixed #92

### Breaking Change
- Updated to require HA 2023.6.  This release requires python 3.11, which is also required by HA 2023.6 and later, so that's the new minimum.

## 3.1.7 2023/02/07
- Fixed #76/#85
- Fixed #77; you can now use {year} and {month} in your URLs to get the current 4 digit year and 2 digit month.
- Fixed #78; you can now specify an offset in hours if your calendar entries have the wrong time zone.

## 3.1.6 2022/12/12
- Handle UTF-8 BOM in calendar data.
- Properly decode UTF-16 calendar data.

## 3.1.5 2022/11/01
- Handle gzip-encoded responses for servers that incorrectly return gzip'd data.  Thanks to @omnigrok for finding the problem and suggesting a fix!

## 3.1.4 2022/10/17
- Fixed a problem with using authentication with multiple calendars.  Thanks to @Romkabouter for finding the problem and suggesting a fix!

## 3.1.3 2022/10/04
- Refactored code for comparing events when getting current event.  This is now consistent between parsers.  Please report problems if short-duration events don't trigger your automations!
- Fixed #64
- Updated dependencies

## 3.1.2 2022/08/16
- Fixed filter bug for events without a description (thanks to jberrenberg for @identifying and fixing it)
- Please note ICS Calendar is now in the default store for HACS!  You don't need to do anything.

## 3.1.1 2022/08/02
### This release is to correct 3.1.0, which should have required HA 2022.7!
- Added new exclude/include filters (See README.md)
- Added new user_agent option
### Breaking Changes!
- As previously noted, "includeAllDay" was deprecated with v2.9.0.  This version removes support for it. Please use "include_all_day" instead!
- Python 3.10 is now required!
- HA 2022.7 is now required!

## 3.1.0 2022/07/22
- Added new exclude/include filters (See README.md)
- Added new user_agent option
### Breaking Changes!
- As previously noted, "includeAllDay" was deprecated with v2.9.0.  This version removes support for it. Please use "include_all_day" instead!
- Python 3.10 is now required!
- HA 2022.7 is now required!

## 3.0.3 2022/07/19
- Fixed #57
- Updated ics dependency to 0.7.2
- Updated icalendar dependency to 4.1.0

## 3.0.2 2022/06/30
- Updated dependencies

## 3.0.1 2022/06/28
- Fixed #54 which I believe was introduced by PR 71887 of home-assisstant/core. This fix reduces some of the aggressive caching, since the HA calendar code now behaves differently. Given the changes, caching the result of async_get_events is undesirable.
- This may also fix #56
- Applied fix from PR 72922 for home-assistant/core to reduce memory copies

## 3.0.0 2022/05/09
- Refactored to use new CalendarEvent and CalendarEntity classes from HA

## 2.9.0 2022/04/19
- Significant refactoring to change how data is cached and when; should resolve #38
- Added new option, download_interval to set the time between downloading the calendar.  Set to a multiple of 15.
- Renamed includeAllDay to be include_all_day to better match other options.
  The old name will continue to work until version 3.1.0.
- This release includes some aggressive data caching, and will consume more memory. However, CPU usage should be signficantly reduced, especially if download_interval is set to a value of 60 or more. A future release will attempt to reduce the memory usage.

## 2.8.2 2022/04/04
- Breaking change! Requires Home Assistant 2022.4 or later
- Fixed bug with error messages
- Fixed #48

## 2.8.1 2022/03/31
- Breaking change! Requires Home Assistant 2022.4 or later
- Fixed code to work with upcoming 2022.4 releases
- Refactored internal code for better test coverage

## 2.8.0 2022/03/31
WITHDRAWN -- See 2.8.1 instead.

## 2.7.0 2022/03/29
- Removed icalevents parser
- Corrected manifest.json and hacs.json

## 2.6.1 2022/03/04
- Added additional output to some error conditions

## 2.6.0 2022/03/01
- Fixed some problems with rie parser
- Added new "days" option so the next event will be shown better (see issues #43 & #44, and PR #33)
- Added more unit tests

## 2.5.0 2022/01/03
- Added new parser, "rie" and made it the default.

## 2.1.2 2022/01/03
- Fixed ics parser

## 2.1.1 2022/01/03
- Fixed deprecated device_state_attributes
- Updated internal code to remove duplicated methods
- Updated unit tests and infrastructure
- Updated minimum HA version to 2021.4.0

## 2.1.0 2021/10/19
- Added code to cache calls to async_get_events, which might reduce CPU usage
- Added code to cache calls to download the calendar data
- Note: the above items are not configurable yet
- Fixed resource leak

## 2.0.0 2021/08/11
- This is a breaking change, even for users of the 2.0 beta releases.  Uninstall and re-install this platform, do not update!
- Calendar platform name has changed; use "ics_calendar" instead of "ics" now
- You can now switch which parser is used on a per-calendar basis; see the parser option in README.md

## 2.0.0-beta12 2021/08/11 (NOT FOR GENERAL USE)
- Internal fixes

## 2.0.0-beta11 2021/08/11 (NOT FOR GENERAL USE)
- Changed platform name to "ics_calendar" to match directory name

## 2.0.0-beta10 2021/08/10 (NOT FOR GENERAL USE)
- Updated code to allow switching parsers based on which calendar, and eliminating the "use the beta" or "use the non-beta" replies
- Added some unit tests
- Fixed #34
- Fixed #35

## 2.0.0-beta9 2021/06/18
- Fixed #30, thanks to dannytrigo.  I believe this one affected only the beta

## 2.0.0-beta8 2021/04/12
- Added version key to manifest.json which is now required by Home Assitant

## 1.0.7 2021/04/12
- Added version key to manifest.json which is now required by Home Assitant

## 2.0.0-beta7 2020/10/20
- Fixed #20

## 1.0.6 2020/10/20
- Improved error handling, based on fixing #20 for the beta version
- Updated imports for arrow (see issue #16)

## 2.0.0-beta6 2020/09/11
- Added support for HTTP Basic Auth and Digest Auth (see issue #13)

## 1.0.5 2020/09/11
- Added support for HTTP Basic Auth and Digest Auth (see issue #13)

## 2.0.0-beta5 2020/09/09
- Fixed issue #15
- Merged PR #14
- Fixed issue #11

## 1.0.4 2020/09/09
- Fixed issue #15
- Merged PR #14
- Documented includeAllDay

## 1.0.3.1 2020/06/05
- Fixed #11
- Fixed I/O to be async properly
- Updated all dates to be local timezone if there's no timezone instead of UTC.

## 1.0.2 2020/02/04
Fixed issue #7

## 1.0.1 2020/01/16
Added work-around for issue #5

## 1.0.0 2019/08/15
Initial release
