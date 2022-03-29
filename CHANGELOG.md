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
