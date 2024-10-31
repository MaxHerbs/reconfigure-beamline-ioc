from cothread.catools import caput, caget, DBR_STRING
from cothread import Sleep
import subprocess
import os
import argparse
import yaml

post_safe_shutdown_wait_time = 10
post_ioc_restart_wait_time = 10
ioc_poll_time = 0.5
ioc_status_timeout = 30 

class IocController():
    def __init__(self, iocYaml):
        """
        IocConfig Constructor

        nickname: Human readable name for the ioc, eg PandA
        iocName: Formal ioc name
        iocPath: Path for new ioc executable
        safeRestart: Used where ioc needs a safe restart

        """
        # Bare minimum ioc detials
        self.nickname = iocYaml.pop("name", None)
        self.iocName = iocYaml.pop("iocName", None)
        self.iocPath = iocYaml.pop("executable", None)

        if not (self.nickname and self.iocName and self.iocPath):
            raise Exception("IOC is missing a name, iocName, or executable path in config.")

        if not os.path.exists(self.iocPath):
            raise Exception(f"IOC {self.iocName} executable could not be found.")

        self.safeRestart = iocYaml.pop("safeRestart", 0)
        
        


    def redirectIoc(self):
        '''
        Changes redirect for ioc

        :returns: null if success, error message if failure
        '''
        print(f"Configuring {self.nickname}")
        result = subprocess.run(
                        ["/dls_sw/prod/tools/RHEL7-x86_64/defaults/bin/configure-ioc",
                         "edit", self.iocName, self.iocPath],
                        capture_output = True,
                        )

        thisError = result.stderr.decode('ASCII')
        thisOut = result.stdout.decode('ASCII')
        if thisError != "":
            print(f"Error occured for {self.iocName} ({self.nickname}) while changing redirector. Further information will be provided at end of script.")
            print(thisError)
            print(thisOut)
            return thisError, thisOut
        else:
            print(f"{self.iocName} successfully redirected")

        return thisError



    
    def restartIoc(self):
        """
        Restarts an individual IOC with either a normal or safe restart.
        Waits and verifies the success of a restart

        :returns: 0 if success, the error if fail

        """
        print(f"Restarting {self.iocName} ({self.nickname})")
        try:
            if self.safeRestart:
                self.doSafeRestart()
            else:
                cmd = self.iocName + ":RESTART"
                print(cmd)
                caput(cmd, "1", wait=False)


            print(f"Waiting...", end="")
            Sleep(post_ioc_restart_wait_time)
            currWait = 0.0
            retries = 0

            iocStatus = self.getIocStatus()
            while iocStatus != "Running":
                print(".", end="")
                Sleep(ioc_poll_time)
                currWait += ioc_poll_time
                iocStatus = self.getIocStatus()
                if not iocStatus:
                    retries += 1
                    if currWait > ioc_status_timeout:
                        return "IOC timed out will restarting. Reboot failed."
                    if retries >= self.ioc_status_max_retries:
                        return "Too many retries while rebooting. Reboot failed."
            print("")
            if iocStatus == "Running":
                print("Successfully restarted")
                return 0
            return "Unsure. Is the IOC running?"

        except Exception as err:
            return str(err)


    def doSafeRestart(self):
        print("Performing a safe restart")

        caput(self.iocName + ":SYSRESET", 1, wait=False)
        if self.getIocAutorestartStatus() != "On":
            Sleep(post_safe_shutdown_wait_time)
            self.startIoc(self.iocName)


    def getIocAutorestartStatus(self):
        return caput(self.iocName + ":AUTORESTART",
                                        datatype=DBR_STRING)
  
    def startIoc(self):
        caput(self.iocName + ":START", 1, wait=False)

    def getIocStatus(self):
        return caget(self.iocName + ":STATUS",
                                       datatype=DBR_STRING)






