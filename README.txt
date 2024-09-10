WTF is this?
============

This is a macOS toolbar application that shows the status of keylime attestation in the production system.

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

* The overall status of the application is red, yellow or green based
on whether there are any red statuses on the JIRA issues it's
following. Green means "all OK"; yellow means "cannot talk to JIRA";
red means "something is broken".

* Click on the colored ball to see details.

* It is possible to set up JIRA issues into the "do not care" state by
  clicking on them in the menu. They turn gray and stop affecting the
  overall status.

* TODO, not implemented: clicking on the "x seconds til next check"
  announcement should cause an immediate refresh.
  

3. How to build this application
===============================

3a. Prerequisites:
--------------
* Have python3 installed on your mac.
* Have python3-pip installed on the mac (cmdline "pip3")
* Have the following python packages installed on the mac (with 'pip3 install')
  - basic packaging tools: requests, packaging, setuptools
  - atlassian Python code: atlassian-python-api
  - macos specific packages: rumps, py2app

3b. Build:
---------

* run ./build.sh
* the process (if successful) results in a DMG file in /tmp/OPVsyndeo.dmg.
* Open the DMG by doubleclicking it; drag the application inside to "Applications" using Finder.
* Doubleclick the application to run it. It will immediately show a yellow


