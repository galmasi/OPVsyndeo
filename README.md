OPVSyndeo
============

sshuttle (https://github.com/sshuttle/sshuttle) is a VPN tool useful
in situations where remote connectivity is through SSH.


OPVsyndeo is a macOS toolbar application that controls multiple
sshuttle sessions. The sessions are defined in an initial
configuration file in JSON format.

Application wide settings include the location of the SSH private key,
particulars of the SSH command to be used by sshuttle, and other
sshuttle settable parameters.

Per-remote-site settings include the target location's IP or hostname,
the network ranges that should be mapped by sshuttle in each case, and
optionally an http URL that can be checked for liveness.

1. How to use this application
===========================

* If you want to build the code from source, please check Section 3.

* Download the DMG from the github releases section; open the DMG on
  your laptop and copy the application itself into the Applications
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

3. Configuration file
=====================

The configuration file shows up in `~/Library/Application
Support/OPVsyndeo/OPVsyndeo.json`. If not present, OPVsyndeo will
create a reasonable default the first time it runs.

```
{
  'sshkey'      : os.environ['HOME'] + '/.ssh/id_rsa',
  'sshoptions'  : '-oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -oBatchMode=yes -oPasswordAuthentication=no -oConnectTimeout=20',
  'sshuttlecmd' : 'sshuttle --disable-ipv6 --dns --python python3',
  'username'    : os.environ['USER'],
  'networks'    : {
    'site1': {
       'jumphost': '<jumphost-address-1>',   <-------- IP or hostname of jump host
        'nets': [ '100.64.0.0/16', '10.42.0.0/16' ], <------- network ranges to map
        'testurl': 'http://100.64.0.255/' <----- url to test
        },
    }
}
```

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

