#!/usr/bin/env python3

import json
import os
import subprocess
import signal
import datetime
import rumps
import configparser
import py2app
import tempfile
import urllib.request
import sshuttle

#urllib3.disable_warnings()
#rumps.debug_mode(True)

class OPVsyndeoApp(object):

    # ###########################################################
    # (model) default configuration
    # ###########################################################

    defaultconfig = {
        'sshkey'      : os.environ['HOME'] + '/.ssh/id_rsa',
        'sshoptions'  : '-oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -oBatchMode=yes -oPasswordAuthentication=no -oConnectTimeout=20',
        'sshuttlecmd' : 'sshuttle --disable-ipv6 --dns --python python3',
        'username'    : os.environ['USER'],
        'networks': {
	    "31lab": {
	        "jumphost": "9.2.220.22",
	        "nets": [
		    "10.20.0.0/16",
		    "10.30.0.0/16"
	        ]
	    },
	    "ykt": {
	        "jumphost": "9.2.130.16",
	        "nets": [
		    "100.64.0.0/16",
		    "10.42.0.0/16",
		    "192.168.16.0/22",
		    "192.168.252.0/22"
	        ],
	        "testurl": "http://100.64.0.255/"
	    },
	    "pokstg": {
	        "jumphost": "9.47.228.15",
	        "nets": [
		    "192.168.92.0/22",
		    "192.168.99.0/22",
		    "192.168.189.0/24",
		    "169.253.0.0/16"
	        ]
	    },
	    "pokcicd": {
	        "jumphost": "9.47.147.38",
	        "nets": [
		    "192.168.92.0/22",
		    "192.168.88.0/22"
	        ]
	    },
	    "pokprod": {
	        "jumphost": "9.47.228.16",
	        "nets": [
		    "192.168.96.0/22"
	        ],
	        "testurl": "http://192.168.98.10/"
	    },
	    "qpokey": {
	        "jumphost": "9.47.228.118",
	        "nets": [
		    "192.168.80.0/22",
		    "192.168.76.0/22"
	        ]
	    },
	    "gaptooth": {
	        "jumphost": "9.47.228.121",
	        "nets": [
		    "192.168.76.0/22"
	        ],
                "testurl": "http://192.168.76.1/"
	    }
        }
    }
    # ###########################################################
    # application initialization
    # -----------------------------------------------------------
    # "shouldrun" is a dictionary that determines whether a network sshuttle should be active or not.
    # "sshuttleprocesses" is the dictionary of all sshuttle "subprocess" objects
    # "sshuttlefiles" is the dictionary of all log files attached to sshuttle processes
    # "menuitems" helps us find a menu item based on the network name key
    # ###########################################################

    def __init__(self):
        self.app = rumps.App("OPVsyndeo", title="", icon='icons/gray.png', quit_button=None)

        # load configuration
        self.config  = self.config_load()

        # set up a sane default environment: put execution location into the default path
        # python resources will be in /Applications/OPVsyndeo.app/Contents/Resources
        myabspath=os.path.dirname(os.path.abspath(__file__))
        resourcepath=myabspath.replace('MacOS','Resources')
        self.myenv = os.environ
        self.myenv['PATH'] = myabspath + ':' + resourcepath + ':/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:' + self.myenv['PATH']

        #self.myenv['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:' + self.myenv['PATH'] 

        # check sudo privileges
        self.config_check_sshuttle_sudo()

        # check private and public keys
        self.config_check_private_key()

        # set up state
        self.shouldrun = {}
        self.menuitems = {}
        self.sshuttle_pids = {}
        self.sshuttlefiles = {}

        # create all menu items
        menulist = []
        for netname in self.config['networks'].keys():
            menuitem = rumps.MenuItem(title="%-10.10s(%s)"%(netname,'idle'), callback=self.toggleActive)
            menuitem.enabled                = True
            menuitem.netname                = netname
            self.menuitems[netname]         = menuitem
            menulist.append(menuitem)
            self.shouldrun[netname]         = False
            self.sshuttle_pids[netname]     = None
            self.sshuttlefiles[netname]     = None
        # horizontal separator
        menulist.append(None)

        # debugging menu item
        menuitem = rumps.MenuItem(title='Show debug console[s]', callback=self.clickDebug)
        menuitem.enabled = True
        menulist.append(menuitem)

        # quit menu item
        menuitem = rumps.MenuItem(title="Quit", callback=self.quit)
        menuitem.enabled = True
        menulist.append(menuitem)

        # remove all log files from previous runs
        for netname in self.config['networks'].keys():
            try:
                os.remove('/tmp/' + netname + '.out')
            except:
                pass

        # setup update timer
        self.timer = rumps.Timer(self.on_tick, 5)
        self.timer.first_tick = True

        # final menu list
        self.app.menu=menulist
        
    # ###########################################################
    # (controller) RUMPS function: run. start the timer, then give up control
    # ###########################################################

    def run(self):
        self.timer.start()
        self.app.run()

    # ###########################################################
    # (controller) RUMPS function: toggle a menu item
    # this gets called when any menu item is clicked upon.
    # we toggle the "shouldrun" boolean for the item then sync status
    # ###########################################################

    def toggleActive(self, menuitem):
        netname=menuitem.netname
        self.shouldrun[netname] = not self.shouldrun[netname]
        self.updatestatus()

    # ###########################################################
    # (controller) RUMPS function: start debug
    # this forces debug windows for all active connections.
    # ###########################################################

    def clickDebug(self, menuitem):
        for netname in self.config['networks'].keys():
            if self.shouldrun[netname] and self.sshuttlefiles[netname] is not None:
                cmd = 'osascript -e \'tell app "Terminal" to do script "tail -f /tmp/' + netname + '.out"\''
                os.system(cmd)

    # ###########################################################
    # (controller) RUMPS function: quit
    # ###########################################################

    def quit(self, menuitem):
        for netname in self.config['networks'].keys():
            self.process_kill(netname)
        rumps.quit_application()

    # ###########################################################
    # (controller) RUMPS function: timer tick
    # ###########################################################

    def on_tick(self, _):
        self.updatestatus()

    # ###########################################################
    # (model) load configuration (hardcoded for now)
    # ###########################################################
    
    def config_load (self):
        self.configdir  = os.environ['HOME'] + '/Library/Application Support/OPVsyndeo'
        self.configfile = self.configdir + '/OPVsyndeo.json'
        if os.access(self.configfile, os.R_OK):
            try:
                fp = open(self.configfile, 'r')
                return json.load (fp)
            except Exception as e:
                rumps.alert (title="Cannot read config file %s"%(self.configfile),
                             message=str(e),
                             ok=None,
                             cancel=None)
                exit(1)
        else:
            defconfigstring = json.dumps(self.defaultconfig, indent=2)
            rumps.alert(title="config file not found. Writing defaults to %s as follows:"%(self.configfile),
                        message=defconfigstring,
                        ok="Continue",
                        cancel=None)
            try:
                os.makedirs(self.configdir, exist_ok=True)
                fp = open(self.configfile, 'w')
                fp.write(defconfigstring)
                fp.close()
                return json.loads(defconfigstring)
            except Exception as e:
                rumps.alert(title="Failed to write config file",
                            message=self.configfile + ": " + str(e),
                            ok="Exit",
                            cancel=None)
                exit(1)

    # ###########################################################
    # check that we have the right privileges to run sshuttle
    # ###########################################################

    def config_check_sshuttle_sudo (self):

        # check whether the sshuttle_auto file exists. Nothing to do if it does.
        sudofilename='/etc/sudoers.d/sshuttle_auto_' + os.environ['USER']
        if os.path.exists(sudofilename): return

        # figure out how the file would look like.
        try:
            cmd = self.config['sshuttlecmd'].split(' ')
            cmd.append('--sudoers-no-modify')
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.myenv)
            p.wait()
            outs, errs = p.communicate()
        except Exception as e:
            rumps.alert(title="failed to run sshuttle",
                        message="check the path to sshuttle in your configuration",
                        ok = "Exit",
                        cancel = None)
            exit(1)
        sudoers_file_content=str(outs.decode())

        # pop up a message asking the user whether they want it set up.        
        warningmessage="sshuttle needs passwordless sudo access, and your system seems to not be configured for it.\n"
        warningmessage += "Do you want this set up now?\n\n"
        warningmessage += "Security note: sshuttle sudo privileges can be abused. YMMV"
        retval = rumps.alert(title="OPVSyndeo Initial Setup",
                             message=warningmessage,
                             ok = "Do it for me now",
                             cancel = "Don't change my system")
        if retval == 0: exit(0)

        # generate a temporary file with the contents
        try:
            fp = tempfile.NamedTemporaryFile(mode='w', delete=False)
            print('sudoers recommendation from sshuttle:\n---')
            print(sudoers_file_content)
            fp.write(sudoers_file_content)
            fp.close()
        except Exception as e:
            rumps.alert(title="Failed to write tempfile. Giving up.",
                        message=str(e),
                        ok = "Exit",
                        cancel = None)
            exit(1)

        # attempt to move file into place
        try:
            cmd = 'osascript -e \'do shell script "sudo mv -f ' + fp.name + ' ' + sudofilename + '" with administrator privileges\''
            os.system(cmd)
        except Exception as e:
            rumps.alert(title="failed to setup sudoers file for sshuttle",
                        message="",
                        ok = "Exit",
                        cancel = None)
            print("done")
            exit(1)

    # ###########################################################
    # (model) check the configuration for consistency
    # ###########################################################

    def config_check_private_key (self):
        if 'sshkey' not in self.config:
            rumps.alert (title="ssh key not defined in configuration",
                         ok = "Exit",
                         cancel = None)
            exit(1)
        if not os.access(self.config['sshkey'], os.R_OK):
            rumps.alert (title="ssh key is not readable",
                         message=self.config['sshkey'],
                         ok = "Exit",
                         cancel = None)
            exit(1)
        
    
    # ###########################################################
    # (model) main status reconciler
    # ###########################################################

    def updatestatus(self):
        symlist = { 'bad': "🔴", 'transient': "🟡", 'running': "🟢",  'idle': "🔘" }
        idle = False
        running = False
        transient = False
        for netname in self.shouldrun.keys():
            if self.shouldrun[netname]:
                if self.process_check(netname):
                    status = "run 🟢"
                    idle = False
                    running = True
                else:
                    status = "starting🟡"
                    idle = False
                    transient = True
                    self.process_start(netname)
            else:
                if self.process_check(netname):
                    status = "stopping🟡"
                    idle = False
                    transient = True
                    self.process_kill(netname)
                else:
                    status = "idle🔘"
                    idle = True
            self.menuitems[netname].title = "%-10.10s(%s)"%(netname,status)

        # determine global status.
        # if any items are transient, we are yellow
        # if there are no transients and at least one item is running, we are green
        # otherwise we are gray.
        if transient: self.app.icon = 'icons/yellow.png'
        if running: self.app.icon = 'icons/green.png'
        else: self.app.icon = 'icons/gray.png'
        
    # ###########################################################
    # (model) start a sshuttle process.
    # composes the command line and calls popen.
    # ###########################################################

    def process_start (self, netname):
        if self.sshuttle_pids[netname] is not None: return
        
        username = self.config['username']
        jhost = self.config['networks'][netname]['jumphost']
        pidfile = '/tmp/' + netname + '.pid'
        nets = self.config['networks'][netname]['nets']
        sshoptions = 'ssh ' + self.config['sshoptions']
        sshoptions += ' -i ' + self.config['sshkey']

        # compose the command
        cmd = self.config['sshuttlecmd'].split(' ')
        cmd.append('-e')
        cmd.append(sshoptions)
        cmd.append('-r')
        cmd.append(username + '@' + jhost)
        cmd.extend(nets)

        print(cmd)

        # start the process
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.myenv)
        self.sshuttle_pids[netname] = p
        os.set_blocking(p.stdout.fileno(), False)
        os.set_blocking(p.stderr.fileno(), False)

        # open the log file
        self.sshuttlefiles[netname] = open('/tmp/'+netname+'.out', 'wb')

    # ###########################################################
    # (model) destroy an sshuttle process.
    # ###########################################################

    def process_kill (self, netname):
        # remove the process, kill it and wait for it.
        if self.sshuttle_pids[netname] is not None:
            try:
                p = self.sshuttle_pids[netname]
                p.kill()
                outs, errs = p.communicate()
                fp.sshuttlefiles[netname].write(outs)
                fp.sshuttlefiles[netname].write(errs)
            except:
                pass
            self.sshuttle_pids[netname] = None

        # close the log file.
        if self.sshuttlefiles[netname] is not None:
            try:
                self.sshuttlefiles[netname].close()
            except:
                pass
            self.sshuttlefiles[netname] = None
            
    # ###########################################################
    # (model) check whether a sshuttle process exists and is healthy
    # --------------------
    # returns true if the process is running and connections check out
    # returns true if the process is running and there is no connection to check
    # returns false if there is no process.
    # returns false and kills the process if the process doesn't poll
    # reads all the available stdout and stderr from any running process
    # ###########################################################

    def process_check (self, netname):
        if self.sshuttle_pids[netname] is None:
            return False
        p = self.sshuttle_pids[netname]
        if p.poll() != None:
            self.process_kill(netname)
            return False
        fp = self.sshuttlefiles[netname]
        while True:
            line1 = p.stdout.readline()
            line2 = p.stderr.readline()
            if len(line1) <= 0 and len(line2) <= 0:
                break
            fp.write(line1)
            fp.write(line2)
            fp.flush()
        return self.checkconnection(netname)


    # ###########################################################
    # (model) check whether a connection is live by pulling the test URL
    # ###########################################################

    def checkconnection (self, netname):
        if self.sshuttle_pids[netname] is None: return False
        try:
            testurl = self.config['networks'][netname]['testurl']
        except:
            # vacuously true, there is no test URL defined
            return True
        try:
            # if we fail anywhere here, it's failed
            response = urllib.request.urlopen(testurl,timeout=1)
            response.read()
        except Exception as e:
            return False
        return True

if __name__ == '__main__':
    app = OPVsyndeoApp()
    app.run()
