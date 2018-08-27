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
    os.system("DistributedComputing\\PushCodebase.bat")


#NOTE: NOT YET IMPLIMENTED
def installPackages(packagesToInstall):
    '''
    Installs or upgrades all the packages listen in packagesToInstall
    Retunrs tuple: (bool success, [results])
    '''
    return (True, ["Monika: Can you hear me?"])


def kill(restart = False):
    '''
    Kills python on this local machine.
    Restarts Bot client if restart == True
    '''
    if (restart):
        os.system("DistributedComputing\\KillAndRestart.bat")
    else:
        os.system("DistributedComputing\\Kill.bat")


def openNewClietWindow():
    '''
    Kills python on this local machine. 
    Starts a new command window with a client terminal
    '''
    os.chdir("DistributedComputing")
    os.system("OpenClientWindow_FromThisDirectory.bat")


def clearLogFolder():
    '''
    Deletes all files inside the Logs folder
    '''
    LOGPRINT("Clearing Logs folder...")
    os.system("del /f /Q DistributedComputing\Logs\*")