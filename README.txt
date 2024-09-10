WTF is this?
============

This is a macOS toolbar application that control sshuttle sessions.

Table of contents
=================

1. How to run this application
2. Interacting with the application
3. How to build this application


1. How to use this application
===========================

* If you want to build the code from source, please check Section 3.

* Open the DMG and copy the application itself into the Applications
  mac folder. Then double-click it to run like you would run any
  normal mac application.

2. Interactions at application runtime
===================================

* This application shows up in the mac menu bar.
* Click on the network you want to activate/deactivate. Clicking toggles the network.
* Idle networks show up in gray.
* Active networks show in in green.
* Networks in transient stage show up in yellow.
* Broken connections show up in red.

3. How to build this application
===============================

3a. Prerequisites:
--------------
* Have python3 installed on your mac.
* Have python3-pip installed on the mac (cmdline "pip3")
* Have the following python packages installed on the mac (with 'pip3 install')
  - basic packaging tools: requests, packaging, setuptools
  - sshuttle
  - macos specific packages: rumps, py2app

3b. Build:
---------

* run ./build.sh
* the process (if successful) results in a DMG file in /tmp/OPVsyndeo.dmg.
* Open the DMG by doubleclicking it; drag the application inside to "Applications" using Finder.


4. Todos
===

* Quit button should kill all networks [DONE]
* No broken networks (no transient time out) -- needs implemented
* Does not work when double clicked.
* No YAML/JSON configuration available. Everything is hardcoded.

