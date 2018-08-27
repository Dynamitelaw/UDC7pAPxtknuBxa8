'''
Dynamitelaw

Utility functions for the DistributedComputing module
'''

#External Imports
import datetime
import time
import socket
import threading
import json
import os

#Custim Imports
from NetworkDefinitions import *


logPrintLock = threading.Lock()

def LOGPRINT(messsage):
    '''
    Add the message to the log file and print to terminal
    '''
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    formattedMessage = socket.gethostname() + " " + timestamp + " # " + str(messsage)
    
    logPath = "DistributedComputing/Logs/" + socket.gethostname() + "_Log.txt"
    logPrintLock.acquire()
    
    with open(logPath, "a") as logfile:
        print(formattedMessage)
        logfile.write(formattedMessage + "\n")
        logfile.close()

    logPrintLock.release()


def DictionaryToString(dictionary):
    '''
    Returns a string representation of a dictionary
    '''
    outputString = "{"

    for key in dictionary:
        outputString += '"' + str(key) + '"'
        outputString += ": "
        outputString += '"' + str(dictionary[key]) + '"'
        outputString += ","

    outputString = outputString[0:-1]
    outputString += "}"

    return outputString


def DictionaryToJson(dictionary):
    '''
    Converts a dictionary to a JSON object
    '''
    return json.dumps(dictionary)


def isValidJson(JsonString):
    '''
    Checks if the passed string is a valid Json
    '''
    try:
        json.loads(JsonString)
        return True
    except:
        return False


from DistributedFunctions import pushCodebase  #This is here to prevent an import loop
def updateLocalMappings():
    '''
    Update local mapping file
    '''
    #Try to parse old mappings
    parsedOldMappings = False
    try:
        with open("DistributedComputing/Mappings/LOCAL.json") as f:
            oldMappings = json.load(f)
            f.close()
        parsedOldMappings = True
    except:
        LOGPRINT("Could not parse previous local mappings. Creating new local mappings")

    #Create new mappings
    localMappings = {}
    localMappings["LocalHostname"] = socket.gethostname()
    localMappings["PublicIp"] = PUBLIC_IP
    if (parsedOldMappings):
        localMappings["FriendlyName"] = oldMappings["FriendlyName"]
    else:
        localMappings["FriendlyName"] = "INTERT_FRIENDLY_NAME_HERE"

    #Save mappings
    localMappingsJsonString = json.dumps(localMappings)

    localMappingFile = open("DistributedComputing/Mappings/LOCAL.json", 'w')
    localMappingFile.write(localMappingsJsonString)
    localMappingFile.close()

    externalMappingFile = open("DistributedComputing/Mappings/" + localMappings["LocalHostname"] + ".json", 'w')
    externalMappingFile.write(localMappingsJsonString)
    externalMappingFile.close()

    #Check for changes in mappings
    if (parsedOldMappings):
        oldPublicIp = oldMappings["PublicIp"]
        if (PUBLIC_IP != oldPublicIp):
            #Update everyone elses IP mappings
            pushCodebase()
    else:
        #No old local mappings were present. Update everyone else
        LOGPRINT("New local mappings = " + localMappingsJsonString)
        pushCodebase()


def updatePeerMappings(peerDictionary):
    '''
    Populate the inputted peer mapping dictionary
    '''
    #Get list of peer hostnames
    fileList = os.listdir("DistributedComputing\Mappings")
    
    peerHostnames = []
    for filename in fileList:
        hostname = filename.rstrip(".json")
        if (filename == "LOCAL.json"):
            pass
        elif (hostname == socket.gethostname()):
            pass
        else:
            peerHostnames.append(hostname)

    for hostname in peerHostnames:
        with open("DistributedComputing/Mappings/" + hostname + ".json") as f:
            peerMappings = json.load(f)
            f.close()
        peerDictionary[hostname] = peerMappings
        LOGPRINT("Added peer mapping: " + str(peerMappings))
        

def parseIncomingMessage(message):
    '''
    Parses the incoming message. Return a dictionary object representing the message
    '''
    messageDict = json.loads(message)
    try:
        messageDict["MessageType"] = PEER_MESSAGE(messageDict["MessageType"])
    except:
        pass
    return messageDict


