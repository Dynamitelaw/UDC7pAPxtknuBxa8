'''
Dynamitelaw

Contains the functions that are called by incomming bot commands
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
    os.system("DistributedNetworking\\UpdateCodebase.bat")
