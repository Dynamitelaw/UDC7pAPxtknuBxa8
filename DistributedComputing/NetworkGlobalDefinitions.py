'''
Dynamitelaw

Definitions for all objects required by the DistributedComputing module
'''

#External imports
from enum import Enum, unique
import socket


#Enum for accepted PeerMessages
@unique
class PeerMessage(Enum):
    #NOTE: DO NOT CHANGE THESE NUMBERS AFTER THEY HAVE BEEN SET
    HEARBEAT_MESSAGE = 0
        #Heartbeat message sent to peer to let them know we're still alive
        #args = NA
    RETURN_MESSAGE = 1
        #Message sent to indicate that the message contains a return value
        #args = NA
    UPDATE_PROJECT_COMMAND = 2
        #Peer will do a git pull to update their project files
        #args = NA
    PUSH_PROJECT_COMMAND = 3
        #Peer will do a git push to update the repo with changes
        #args = NA
    KILL_CLIENT_COMMAND = 4
        #Peer will kill itself, and end all python processes
        #args = (bool restartAfterKill)


#Networking globals
LOCAL_IP = socket.gethostbyname(socket.gethostname())
PORT_LISTEN = 25700
BUFFER_SIZE = 4096

#Timeout globals
HEARBEAT_INTERVAL = 10
OUTBOUND_RETRY_INTERVAL = 60