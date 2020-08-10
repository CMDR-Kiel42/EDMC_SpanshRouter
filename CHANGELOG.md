# EDMC_SpanshRouter Change Log

All notable changes to this project will be documented in this file.

## 3.1.0

- BE ADVISED: This version only works for EDMC 4.0.0.0 and above. Do not install if you're not currently running the latest EDMC version.
- Fixed a bug with csv file containing system names in uppercase
- Fixed a bug where the suggestions list would linger on the main screen

## 3.0.4

- BE ADVISED: This version only works for EDMC 4.0.0.0 and above. Do not install if you're not currently running the latest EDMC version. This will be left as e pre-release for some time to let everyone update EDMC.
- Dropped support for previous EDMC versions
- Fixed bugs with the autocompleted fields in the "plot route" interface

## 3.0.3

- Fixed "no previously saved route" message even though a saved route was present
- Allow single click selection in the "Plot route" interface
- Fixed update issue when using Python 3

## 3.0.2

- Fixed an issue where the update popup would crash EDMC

## 3.0.1

- Fixed issues with Python 2

## 3.0.0

- Add compatibility with the Python 3 version of EDMC
- Fixed an issue with CSV files containing a BOM code (added by some programs such as Microsoft Excel)
- When browsing to import a file, set starting directory at user's home

## 2.2.1

- Changes from updates now appear in a popup so the user can choose wether they want to install it or not.

## 2.2.0

- Now supports any CSV having columns named "System Name" and "Jumps". The "Jumps" column is optional
- Supports text files given by EDTS (it is the only .txt file supported for now)
- The "Start System" in the potter is now automatically set to the one you are currently in
- Fixed a bug where the plugin could make EDMC crash by accessing TkInter state in a thread

## 2.1.4

- Autosaves your progress more often in case EDMC crashes
- Add a right click menu for copy/pasting in the system entries
- Better themes integration

## 2.1.3

- Bugfix: System suggestions actually show up when you type in either Source or Destination system inputs on Windows

## 2.1.2

- Fixed conflicts when other plugins used similar file names
- Fixed plugin sometimes just breaking when nasty errors occured and actually recover from them
- Remove trailing whitespaces when plotting a route to avoid issues with Spansh
- Show plotting errors in the GUI (like unknown system name or invalid range)
- Fixed an issue with the systems list where it wouldn't disappear
- Fixed an issue when plotting from the system you're currently in (it should now *finally* start at the next waypoint)
- Keep previous entries in the *Route plotting* GUI when closing it

## 2.1.1

- Fixed an issue with CSV files containing blank lines

## 2.1.0

- Automatically download and install updates
- Right clicking on a System input now pastes what's in your clipboard

## 2.0.1

- Add an error prompt when things go wrong while plotting a route
- Add requests timeout to prevent the plugin from hanging
- Better recovery from errors

## 2.0.0

- You can now plot your route directly from EDMC
- A few bugs were fixed

## 1.2.1

- Added update button which opens the releases page

## 1.2.0

- Added "Clear route" button
- Added an estimated "jumps left" count
- Better GUI layout
- Better "route save" handling
- Bug fixes

## 1.1.0

- Added "next/previous waypoint" buttons
- Added update notification
- Better route save handling
- Fixed first waypoint not copied when using new route
- Added workarounds for an issue where the first waypoint is not copied/updated

## 1.0.0

- Initial release

