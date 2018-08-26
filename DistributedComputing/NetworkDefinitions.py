'''
Dynamitelaw

Definitions for all objects required by the DistributedComputing module
'''

#External imports
from enum import Enum, unique
import socket
from urllib.request  import urlopen
import json


#-------------------
# Message Format
#-------------------
'''
All messages sent between peers are in the following JSON format
{
    "MessageType": int,             //Required
    "Broadcast": bool,              //Required
    "BroadcastID": int,             //Required. If Broadcast is False, then the ID is 0
    "TargetIP": string,             //Required. Set to "ALL" to target all peers
    "GenericMessage": string,       //Contextual: if GENERIC_MESSAGE
    "SubscriptionID": int,          //Contextual: if sender wants all messages related to this action to be marked as a group to subscribe to. Similar to subject line of an email
    "CommandArguments":             //Needed if the command message requires arguments 
    [
        arg1, arg2, ...
    ],
    "ReturnValues" :                //Contextual: if RETURN_MESSAGE
    [
        returnResult1, returnResult2, ..
    ],
    "CommandSucess" : bool,         //Contextual: if RETURN_MESSAGE
}
'''


#Enum for accepted PeerMessages
@unique
class PEER_MESSAGE(Enum):
    #NOTE: DO NOT CHANGE THESE NUMBERS AFTER THEY HAVE BEEN SET
    HEARBEAT_MESSAGE = 0
        #Heartbeat message sent to peer to let them know we're still alive
        #args = NA
    GENERIC_MESSAGE = 1
        #Generic message sent to peer to print to logs
        #args = NA
    RETURN_MESSAGE = 2
        #Message sent to indicate that the message contains a return value
        #args = NA
    UPDATE_PROJECT_COMMAND = 3
        #Peer will do a git pull to update their project files, then restart
        #args = NA
    PUSH_PROJECT_COMMAND = 4
        #Peer will do a git push to update the repo with changes
        #args = NA
    INSTALL_PACKAGES_COMMAND = 5
        #Peer will pip install specified packages, then restart
        #args = [string packageName1, string packageName2, ...]
    KILL_CLIENT_COMMAND = 6
        #Peer will kill itself, and end all python processes
        #args = [bool restartAfterKill]
    CLEAR_LOGS_COMMAND = 7
        #Peer will delete all Logs in their Logs folder
        #args = NA


#Networking globals
LOCAL_IP = socket.gethostbyname(socket.gethostname())
PUBLIC_IP = json.load(urlopen('https://api.ipify.org/?format=json'))['ip']
PORT_LISTEN = 25700
BUFFER_SIZE = 4096

#Timeout globals
HEARBEAT_INTERVAL = 10
OUTBOUND_RETRY_INTERVAL = 60
SEND_PENDINGS_DELAY = 20