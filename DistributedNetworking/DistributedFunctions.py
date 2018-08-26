'''
Dynamitelaw

Contains the functions that are called by incomming bot commands
'''

#External imports
import os


def updateCodebase():
    '''
    Updates the codebase by doing a git pull.
    Kills current thread
    '''
    print("Updating")
