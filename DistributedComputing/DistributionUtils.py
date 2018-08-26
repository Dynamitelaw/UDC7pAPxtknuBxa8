'''
Dynamitelaw

Utility functions for the Distributed Network module
'''

#External Imports
import datetime
import time
import socket
import threading
import json
import os
from urllib.request  import urlopen


logPrintLock = threading.Lock()

def LOGPRINT(messsage):
    '''
    Add the message to the log file and print to terminal
    '''
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    formattedMessage = socket.gethostname() + " " + timestamp + " # " + str(messsage)
    
    logPath = "DistributedComputing/Logs/" + socket.gethostname() + "_Log.txt"
    logPrintLock.acquire()
    
    with open(logPath, "a") as myfile:
        print(formattedMessage)
        myfile.write(formattedMessage + "\n")
        myfile.close()

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


from DistributedFunctions import pushCodebase
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
    currentPublicIp = json.load(urlopen('https://api.ipify.org/?format=json'))['ip']
    localMappings["PublicIp"] = currentPublicIp
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
        if (currentPublicIp != oldPublicIp):
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
        # elif (hostname == socket.gethostname()):
        #     pass
        else:
            peerHostnames.append(hostname)

    for hostname in peerHostnames:
        with open("DistributedComputing/Mappings/" + hostname + ".json") as f:
            peerMappings = json.load(f)
            f.close()
        peerDictionary[hostname] = peerMappings
        LOGPRINT("Added peer mapping: " + str(peerMappings))


