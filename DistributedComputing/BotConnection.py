'''
Dynamitelaw

Starts a peer client on this machine when run
'''

#External Imports
import sys
import socket
import threading
from time import sleep
from random import randint

#Custom Imports
sys.path.append("./")
import SystemPathImports
from DistributionUtils import *
from DistributedFunctions import *
from NetworkDefinitions import *
import SendPeerCommands


#Define global variables
peerMappings = {}
peerMappingsLock = threading.Lock()

openConnections = {}
openConnectionsLock = threading.Lock()

LocalSubscriptions = {}
localSubscriptionsLock = threading.Lock()

PendingOutboundMessages = []


class Connection():
    '''
    Handles a single two-way connection with another node
    '''
    def __init__(self, connection, bufferSize, addr):
        '''
        Connection constructor
        '''
        self.connectionSocket = connection
        self.bufferSize = bufferSize
        self.peerAddress = addr
        self.peerIp = self.peerAddress[0] 
        self.peerPort = self.peerAddress[1] 
        self.heartBeatRunning = False
        self.hearBeatEnabled = True
        self.peerName = "null"
        self.relayedBroadcasts = []
        self.createHeartbeatMessage()

        LOGPRINT("New Connection object created. Starting incoming handler thread...")

        #Add this connection object to the openConnection dictionary
        #  Look for hostname associated with this IP address
        foundMatchingHostname = False
        peerMappingsLock.acquire()
        for peerHostname in peerMappings:
            mappings = peerMappings[peerHostname]
            if (mappings["PublicIp"] == self.peerAddress[0]):
                #IP address matches. Associate connection with this peer
                foundMatchingHostname = True
                self.peerName = peerHostname + str(self.peerPort)

                openConnectionsLock.acquire()
                openConnections[peerHostname] = self
                openConnectionsLock.release()

                break
        peerMappingsLock.release()

        if (not foundMatchingHostname):
            #This is not a recognized peer. Associate with guest session
            guestHostname = "GUEST_" + str(self.peerIp) + ":" + str(self.peerPort)
            self.peerName = guestHostname
            openConnectionsLock.acquire()
            openConnections[guestHostname] = self
            openConnectionsLock.release()

        
        #Start handling thread
        incomingHandlingThread = threading.Thread(target=self.incommingConnectionThread, args=())
        incomingHandlingThread.start()


    def incommingConnectionThread(self):
        '''
        Handles incomming messages
        '''
        #Start a heartbeat thread for this connection
        if ((not self.heartBeatRunning) and self.hearBeatEnabled):
            heartbeatThread = threading.Thread(target=self.startHeatbeatThread,args=(self.connectionSocket,))
            heartbeatThread.start()

        while True:
            incommingMessage = NULL_STR
            try:
                incommingMessage = str(self.connectionSocket.recv(self.bufferSize))
                firstCharacter = incommingMessage[0]

                while True:
                    if (isValidJson(incommingMessage)):
                        #Entire message has been recieved
                        break
                    elif (firstCharacter != "{"):
                        #This is not an incoming json. Don't wait for more data
                        break
                    else:
                        #Missing part of message
                        sleep(0.5)
                        incommingMessage += str(self.connectionSocket.recv(self.bufferSize))

            except Exception as e:
                LOGPRINT(str("("+self.peerName+")") + " SOCKET ERROR: " + str(e))
                LOGPRINT("("+self.peerName+")" + " Closing socket " + str(self.peerAddress))
                del openConnections[self.peerName]
                LOGPRINT("Open connections: " + DictionaryToString(openConnections))
                return

            if (incommingMessage != NULL_STR):
                if (incommingMessage != "b''"):  #This message seems to be sent repeatedly whenever the peer closes the connection
                    LOGPRINT("("+self.peerName+")" + " >> Msg received: " + incommingMessage)
                    response = self.handleIncommingMessage(incommingMessage)
                    if (response):
                        LOGPRINT("("+self.peerName+")" + " Responding to message")
                        self.connectionSocket.sendall(response.encode('utf-8'))


    def createHeartbeatMessage(self):
        '''
        Creates the heartbeat message for this connection
        '''
        messageDict = {}
        messageDict["MessageType"] = int(PEER_MESSAGE.HEARBEAT_MESSAGE.value)
        messageDict["Broadcast"] = False
        messageDict["BroadcastID"] = 0
        messageDict["TargetIP"] = self.peerIp

        messageJsonString = DictionaryToJson(messageDict)

        self.heartbeatMessage = messageJsonString


    def startHeatbeatThread(self, connection):
        '''
        Starts a heartbeat thread with the connection to tell the other party we're still alive
        '''
        self.heartBeatRunning = True
        try:
            while True:
                connection.sendall(self.heartbeatMessage.encode('utf-8'))
                sleep(HEARBEAT_INTERVAL)
        except:
            pass


    def handleIncommingMessage(self, incommingMessage):
        '''
        Handle incomming messages
        '''
        handlerReturnValue = False

        #Parse incoming message
        messageDict = {}
        try:
            messageDict = parseIncomingMessage(incommingMessage)
        except Exception as e:
            LOGPRINT("("+self.peerName+")" + " ERROR parsing incoming message: " + str(e))
            return False

        MessageType = messageDict["MessageType"]
        Broadcast = messageDict["Broadcast"]
        BroadcastID = messageDict["BroadcastID"]
        TargetIP = messageDict["TargetIP"]

        #Check target IP to see if this message is addressed to us
        WeAreTarget = False
        if ((TargetIP == PUBLIC_IP) or (TargetIP == IP_ALL_STR)):
            WeAreTarget = True
        else:
            WeAreTarget = False

        #Only handle if we haven't already
        if (not Broadcast) or (Broadcast and (not (BroadcastID in self.relayedBroadcasts))):  #Only handle if this message is not a broadcast or it IS a broadcast but we haven't handled it yet
            #Handle message if we're the target
            if (WeAreTarget):
                #If you want to add a new function command to the bot connection, you must handle it here <COMENTFLAG=ADDING_NEW_BOT_FUNCTIONALITY>

                #HEARBEAT_MESSAGE
                if (MessageType == PEER_MESSAGE.HEARBEAT_MESSAGE):
                    pass
                #GENERIC_MESSAGE
                elif (MessageType == PEER_MESSAGE.GENERIC_MESSAGE):
                    if ("GenericMessage" in messageDict):
                        LOGPRINT("("+self.peerName+")" + " " + str(messageDict["GenericMessage"]))
                    else:
                        LOGPRINT("("+self.peerName+")" + " FORMAT ERROR: Missing \"GenericMessage\"")
                #RETURN_MESSAGE
                elif (MessageType == PEER_MESSAGE.RETURN_MESSAGE):
                    if ("ReturnValues" in messageDict):
                        ReturnValues = messageDict["ReturnValues"]
                        if ("SubscriptionID" in messageDict):
                            #Someone has subscribed to this event. Pass message dictionary to be handled by subscriber
                            subscriptionID = messageDict["SubscriptionID"]
                            localSubscriptionsLock.acquire()

                            if (subscriptionID in LocalSubscriptions):
                                subscriptionHandler = LocalSubscriptions[subscriptionID]
                                try:
                                    returnDict = messageDict.copy()
                                    subscriptionHandler.handleReturnMessage(returnDict)
                                except Exception as e:
                                    LOGPRINT("("+self.peerName+")" + " Subscription handler error: " + str(e))

                            localSubscriptionsLock.release()
                    else:
                        LOGPRINT("("+self.peerName+")" + " FORMAT ERROR: Missing \"ReturnValues\"")
                #UPDATE_PROJECT_COMMAND
                elif (MessageType == PEER_MESSAGE.UPDATE_PROJECT_COMMAND):
                    updateCodebase()
                #PUSH_PROJECT_COMMAND
                elif (MessageType == PEER_MESSAGE.PUSH_PROJECT_COMMAND):
                    pushCodebase()
                #INSTALL_PACKAGES_COMMAND
                elif (MessageType == PEER_MESSAGE.INSTALL_PACKAGES_COMMAND):
                    if ("CommandArguments" in messageDict):
                        packagesToInstall = messageDict["CommandArguments"]
                        commandSuccess, results = installPackages(packagesToInstall)

                        handlerReturnValue = self.createCommandResponseMessage(messageDict, commandSuccess, results)
                    else:
                        LOGPRINT("("+self.peerName+")" + " FORMAT ERROR: Missing \"CommandArguments\"")
                        commandSuccess = False
                        results = ["FORMAT ERROR: Missing \"CommandArguments\""]

                        handlerReturnValue = self.createCommandResponseMessage(messageDict, commandSuccess, results)
                #KILL_CLIENT_COMMAND
                elif (MessageType == PEER_MESSAGE.KILL_CLIENT_COMMAND):
                    if ("CommandArguments" in messageDict):
                        restartAfterKill = messageDict["CommandArguments"][0]
                        kill(restartAfterKill)
                    else:
                        LOGPRINT("("+self.peerName+")" + " FORMAT ERROR: Missing \"CommandArguments\"")
                        commandSuccess = False
                        results = ["FORMAT ERROR: Missing \"CommandArguments\""]

                        handlerReturnValue = self.createCommandResponseMessage(messageDict, commandSuccess, results)
                #CLEAR_LOGS_COMMAND
                elif (MessageType == PEER_MESSAGE.CLEAR_LOGS_COMMAND):
                    clearLogFolder()

                #URECOGNIZED MESSAGE TYPE
                else:
                    genericMessage = "Unrecongnized message type: " + str(MessageType)
                    LOGPRINT("("+self.peerName+") " + genericMessage)
                    handlerReturnValue = self.createGenericResponseMessage(messageDict, genericMessage)

            else:
                #We are not the target. Ignoring message
                LOGPRINT("("+self.peerName+")" + " Local client not the message target. Dropping message")


            #Broadcast message if required
            if (Broadcast):
                LOGPRINT("Broadcasting message to connected peers")
                openConnectionsLock.acquire()
                for connectionName in openConnections:
                    openConnections[connectionName].sendMessage(incommingMessage)
                openConnectionsLock.release()
                #Add this broadcastID to relayedBroadcasts list
                self.relayedBroadcasts.append(BroadcastID) 


        #Respond to sender if needed
        if (handlerReturnValue):
            return handlerReturnValue
        else:
            return False


    def sendMessage(self, message):
        '''
        Send the passed message out the connection socket
        '''
        self.connectionSocket.sendall(str(message).encode('utf-8'))

    
    def createCommandResponseMessage(messageDict, commandSuccess, results):
        '''
        Creates a response message for the executed command
        '''
        responseDict = {}
        responseDict["MessageType"] = PEER_MESSAGE.RETURN_MESSAGE.value
        responseDict["Broadcast"] = True
        responseDict["BroadcastID"] = randint(1, MAX_BROADCAST_ID)

        if ("ReturnIP" in messageDict):
            responseDict["TargetIP"] = messageDict["ReturnIP"]
        else:
            responseDict["TargetIP"] = IP_ALL_STR

        if ("SubscriptionID" in messageDict):
            responseDict["SubscriptionID"] = messageDict["SubscriptionID"]

        responseDict["CommandSucess"] = bool(commandSuccess)
        responseDict["ReturnValues"] = results

        responseString = DictionaryToJson(responseDict)

        return(responseString)


    def createGenericResponseMessage(messageDict, genericMessage):
        '''
        Creates a response message for the executed command
        '''
        responseDict = {}
        responseDict["MessageType"] = PEER_MESSAGE.GENERIC_MESSAGE.value
        responseDict["Broadcast"] = True
        responseDict["BroadcastID"] = randint(1, MAX_BROADCAST_ID)

        if ("ReturnIP" in messageDict):
            responseDict["TargetIP"] = messageDict["ReturnIP"]
        else:
            responseDict["TargetIP"] = IP_ALL_STR

        if ("SubscriptionID" in messageDict):
            responseDict["SubscriptionID"] = messageDict["SubscriptionID"]

        responseDict["GenericMessage"] = genericMessage

        responseString = DictionaryToJson(responseDict)

        return(responseString)


    def __str__(self):
        '''
        String representation of connection object
        '''
        return (str(self.peerAddress))
    
    # End Connection class
#=======================================================================
        

def createOutgoingConnections():
    '''
    Continuosuly tries to create outgoing connections to all known peers
    '''
    peersToConnectTo = {}

    #Loop continuously
    while True:
        #Determine which peers we still need to connect to
        peerMappingsLock.acquire()
        openConnectionsLock.acquire()
        for peerHostname in peerMappings:
            if (peerHostname in openConnections):
                #Already connected to this peer. No need to connect
                pass 
            else:
                #Not yet connected to this peer. Add it to connection queue
                peersToConnectTo[peerHostname] = peerMappings[peerHostname]
                
        openConnectionsLock.release()

        for peerName in peersToConnectTo:
            peerMap = peerMappings[peerName]
            peerIP = peerMap["PublicIp"]
            peerFriendlyName = peerMap["FriendlyName"]

            #Establish outbound connection if not already connected
            outbound = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            while True:
                try:
                    outbound.bind((LOCAL_IP, 0))
                    break
                except Exception as e:
                    sleep(2)

            try:
                outbound.connect((peerIP,PORT_LISTEN))
                LOGPRINT("Successfully created connection with " + peerFriendlyName + ":" + peerName + " " + peerIP)
                
                #Instantiate Connection object, which will add itself to openConnections dictionary
                Connection(outbound, BUFFER_SIZE, (peerIP, PORT_LISTEN))
                del peersToConnectTo[peerName]  #Remove peer from connection queue
            except Exception as e:
                LOGPRINT("Could not connect to "+peerName+"("+peerFriendlyName+"):"+peerIP+" | "+str(e)+". Retrying in "+ str(OUTBOUND_RETRY_INTERVAL)+" seconds")

        peerMappingsLock.release()
        sleep(OUTBOUND_RETRY_INTERVAL)


def connectToPeers():
    '''
    Tries to create an outgoing connection to all known peers
    '''
    outgoingConnectionThread = threading.Thread(target=createOutgoingConnections,args=())
    outgoingConnectionThread.start()


def listenForIncommingConnections():
    '''
    Listens for incomming connection requests
    '''

    incomingHost = ''
    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Tries to bind the incoming port
    try:
        listen.bind((incomingHost, PORT_LISTEN))
        LOGPRINT("Listening socket bound to port: " + str(PORT_LISTEN))
    except Exception as e:
        LOGPRINT("Error: " + str(e))
        LOGPRINT("Ending client")
        listen.close()
        return

    listen.listen(5)

    #Listens for incoming connection requests
    while True:
        connection, addr = listen.accept()

        LOGPRINT("Connection established with " + str(addr[0]) + ":" + str(addr[1]))

        #Opens new thread for each client
        Connection(connection, BUFFER_SIZE, addr)
        LOGPRINT("Open connections: " + DictionaryToString(openConnections))


def sendPendingMessages():
    '''
    Broadcast all messages currently in PendingOutboundMessages list
    '''
    for message in PendingOutboundMessages:
        for connectionName in openConnections:
            connectionObject = openConnections[connectionName]
            LOGPRINT("Sending outbound message: " + message)
            connectionObject.sendMessage(message)
        sleep(POST_COMMAND_SLEEP)


if __name__ == '__main__':
    LOGPRINT("\n\n")
    LOGPRINT("----------------------------------------------")
    LOGPRINT("Starting new client")
    LOGPRINT("----------------------------------------------")

    #Update Mappings
    updateLocalMappings()
    updatePeerMappings(peerMappings)

    #Populate subscriptions and outbound messages
    SendPeerCommands.setSubscritptionsAndPendingOutbounds(LocalSubscriptions, PendingOutboundMessages)
    LOGPRINT("Local Subscripctions: " + str(LocalSubscriptions))
    LOGPRINT("Pending Outbound Messages: " + str(PendingOutboundMessages))

    #Initiate and listen for connections
    connectToPeers()
    listeningThread = threading.Thread(target=listenForIncommingConnections, args=())
    listeningThread.start()

    #Send pending outbound messages
    sleep(SEND_PENDINGS_DELAY)
    sendPendingMessages()


