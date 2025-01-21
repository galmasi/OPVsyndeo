Whaat is OPVSyndeo?
===================

OPVsyndeo is a MacOS toolbar application that controls multiple
concurrent sshuttle sessions. The possible sessions are defined in an
initial configuration file in JSON format.

OK, so what is sshuttle?
========================

sshuttle (https://github.com/sshuttle/sshuttle) is a VPN tool useful
in situations where punching through the remote firewall is done by
SSH to the VPN's IP.

I have sshuttle already, why do I need OPVsyndeo?
=================================================

You can run multiple pre-programmed sshuttle sessions. The
"programming" sits in your OPVSyndeo configuration file, typically
located here:

${HOME}/Library/Application Support/OPVSyndeo/OPVSyndeo.json

* Application wide settings include the location of the SSH private key,
particulars of the SSH command to be used by sshuttle, and other
sshuttle settable parameters.

* Per-remote-site settings include the target location's IP or hostname,
the network ranges that should be mapped by sshuttle in each case, and
optionally an http URL that can be checked for liveness.

Starting up OPVSyndeo
=====================

Download the MacOS binary (OPVSyndeo.dmg) to your machine and
double-click it. This should bring up a window with the OPVSyndeo
application in it. Drag the OPVSyndeo application to Applications, and
pacify the system when it complains about security and downloads from
the internet (rightclick -> Open might do the trick). After all this,
double-clicking in the Launcher will work.

Upon first starting up, OPVSyndeo will attempt to find a configuration
file and create one if it can't find it. Since your SSH private keys
may not be where OPVSyndeo is looking, you might want to shut down the
application, edit your configuration file and then restart.

sshuttle needs sudo access to run correctly. OPVSyndeo checks the
existence of a file called /etc/sudoers.d/sshuttle_auto; if the file
is not present OPVSyndeo queries sshuttle for what the contents of
this file should be and presents it to the user. However, OPVSyndeo
will *not* make this change by itself since it involves sudo privileges.

*NOTE* that running sshuttle with sudo privileges is inherently
dangerous, since a clever user could subvert the sshuttle command line
to run basically anything with sudo privileges. Caveat
emptor. OPVSyndeo is not any safer than sshuttle.

I don't trust your binary; I want to build it myself.
======================================================

* Have python3 installed on your mac.
* Have python3-pip installed on the mac (cmdline "pip3")
* Have the following python packages installed on the mac (with 'pip3 install')
  - basic packaging tools: requests, packaging, setuptools
  - sshuttle
  - macos specific packages: rumps, py2app
* With the prerequisites as above, you can always just run ./OPVsyndeo.py
* To build the DMG yourself, run ./build.sh
  * the process (if successful) results in a DMG file in /tmp/OPVsyndeo.dmg.
  * Open the DMG by doubleclicking it; drag the application inside to "Applications" using Finder.

Interacting with OPVSyndeo
==========================

* This application shows up in the mac menu bar.
* Click on the network you want to activate/deactivate. Clicking toggles the network.
* Idle networks show up in gray.
* Active networks show in in green.
* Networks in transient stage show up in yellow.
* Broken connections show up in red.

Configuration file
==================

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

Todos
---

* No broken networks (no transient time out) -- needs implemented

