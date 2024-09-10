#!/bin/bash

rm -rf dist build
rm -f /tmp/OPVsyndeo.dmg
rm -f /tmp/tmp.dmg
python3 setup.py py2app
cp README.txt dist
hdiutil create /tmp/tmp.dmg -ov -volname OPVsyndeo -fs HFS+ -srcfolder "${PWD}/dist"
hdiutil convert /tmp/tmp.dmg -format UDZO -o /tmp/OPVsyndeo
