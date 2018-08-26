'''
Dynamitelaw

Contains the functions that are called by incomming commands
'''

#External imports
import os

#Custom imports
from DistributionUtils import LOGPRINT


def updateCodebase():
    '''
    Updates the codebase by doing a git pull.
    Kills current thread
    '''
    LOGPRINT("Pulling sourcecode from git")
    os.system("DistributedComputing\\UpdateCodebase.bat")


def pushCodebase():
    '''
    Pushes any local changes to the codebase
    '''
    LOGPRINT("Pushing changes to git")
    #os.system("git push")


def kill(restart = False):
    '''
    Kills python on this local machine.
    Restarts Bot client if restart == True
    '''
    if (restart):
        os.system("DistributedComputing\\KillAndRestart.bat")
    else:
        os.system("DistributedComputing\\Kill.bat")