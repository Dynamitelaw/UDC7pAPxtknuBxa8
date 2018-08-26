'''
Dynamitelaw

Starts a peer client on this machine when run
'''

#External Imports
import socket
import threading
from time import sleep

#Custom Imports
from DistributionUtils import *
from DistributedFunctions import *
from NetworkDefinitions import *


#Define global variables
peerMappings = {}
peerMappingsLock = threading.Lock()

openConnections = {}
openConnectionsLock = threading.Lock()


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
        self.peerSocket = self.peerAddress[1] 
        self.heartBeatRunning = False
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
                self.peerName = peerHostname

                openConnectionsLock.acquire()
                openConnections[peerHostname] = self
                openConnectionsLock.release()

                break

        if (not foundMatchingHostname):
            #This is not a recognized peer. Associate with guest session
            guestHostname = "GUEST_" + str(self.peerSocket)
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
        if (not self.heartBeatRunning):
            heartbeatThread = threading.Thread(target=self.startHeatbeatThread,args=(self.connectionSocket,))
            heartbeatThread.start()

        while True:
            incommingMessage = ""
            try:
                incommingMessage = self.connectionSocket.recv(self.bufferSize)
            except Exception as e:
                LOGPRINT(str(self.address) + " socket error: " + str(e))
                LOGPRINT("Closing socket" + str(self.address))
                del openConnections[self.peerName]
                return

            if (len(incommingMessage)):
                LOGPRINT(self.peerName + " >> Msg received: " + str(incommingMessage))
                response = self.handleIncommingMessage(str(incommingMessage))
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
        while True:
            connection.sendall(self.heartbeatMessage.encode('utf-8'))
            sleep(HEARBEAT_INTERVAL)


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
            LOGPRINT("Error parsing incoming message: " + str(e))
            return("ERROR")

        MessageType = messageDict["MessageType"]
        Broadcast = messageDict["Broadcast"]
        BroadcastID = messageDict["BroadcastID"]
        TargetIP = messageDict["TargetIP"]

        #Check target IP to see if this message is addressed to us
        WeAreTarget = False
        if ((TargetIP == PUBLIC_IP) or (TargetIP == "ALL")):
            WeAreTarget = True
        else:
            WeAreTarget = False

        #Only handle if we haven't already
        if (not Broadcast) or (Broadcast and (not (BroadcastID in self.relayedBroadcasts))):  #Only handle if this message is not a broadcast or it IS a broadcast but we haven't handled it yet
            #Handle message if we're the target
            if (WeAreTarget):
                #HEARBEAT_MESSAGE
                if (MessageType == PEER_MESSAGE.HEARBEAT_MESSAGE):
                    pass
                #GENERIC_MESSAGE
                elif (MessageType == PEER_MESSAGE.GENERIC_MESSAGE):
                    if ("GenericMessage" in messageDict):
                        LOGPRINT(messageDict["GenericMessage"])
                    else:
                        LOGPRINT("Format error: Missing \"GenericMessage\"")
                #RETURN_MESSAGE
                elif (MessageType == PEER_MESSAGE.RETURN_MESSAGE):
                    if ("ReturnValues" in messageDict):
                        ReturnValues = messageDict["ReturnValues"]
                        if ("SubscriptionID" in messageDict):
                            #Someone has subscribed to this event. Pass message to subscription service to be handled by subscriber
                            pass
                    else:
                        LOGPRINT("Format error: Missing \"ReturnValues\"")
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
                        LOGPRINT("Format error: Missing \"CommandArguments\"")
                        commandSuccess = False
                        results = ["Format error: Missing \"CommandArguments\""]

                        handlerReturnValue = self.createCommandResponseMessage(messageDict, commandSuccess, results)
                #KILL_CLIENT_COMMAND
                elif (MessageType == PEER_MESSAGE.KILL_CLIENT_COMMAND):
                    if ("CommandArguments" in messageDict):
                        restartAfterKill = messageDict["CommandArguments"][0]
                        kill(restartAfterKill)
                    else:
                        LOGPRINT("Format error: Missing \"CommandArguments\"")
                        commandSuccess = False
                        results = ["Format error: Missing \"CommandArguments\""]

                        handlerReturnValue = self.createCommandResponseMessage(messageDict, commandSuccess, results)
                #CLEAR_LOGS_COMMAND
                elif (MessageType == PEER_MESSAGE.CLEAR_LOGS_COMMAND):
                    clearLogFolder()

                #URECOGNIZED MESSAGE TYPE
                else:
                    genericMessage = "Unrecongnized message type: " + str(MessageType)
                    LOGPRINT(genericMessage)
                    handlerReturnValue = self.createGenericResponseMessage(messageDict, genericMessage)


            #Broadcast message if required
            if (Broadcast):
                openConnectionsLock.acquire()
                for connectionName in openConnections:
                    openConnections[connectionName].sendMessage(incommingMessage)
                openConnectionsLock.release()
                #Add this broadcastID to relayedBroadcasts list
                self.relayedBroadcasts.append(BroadcastID) 


        #Return message to sender if needed
        if (handlerReturnValue):
            return handlerReturnValue
        else:
            return


    def sendMessage(message):
        '''
        Send the passed message out the connection socket
        '''
        self.connectionSocket.sendall(str(message).encode('utf-8'))


    def __str__(self):
        '''
        String representation of connection object
        '''
        return (str(self.peerAddress))
    
    ### End Connection class
        

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
    LOGPRINT("TCP socket created")

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


if __name__ == '__main__':
    LOGPRINT("\n\n")
    LOGPRINT("----------------------------------------------")
    LOGPRINT("Starting new client")
    updateLocalMappings()
    updatePeerMappings(peerMappings)
    connectToPeers()
    listenForIncommingConnections()
    sleep(SEND_PENDINGS_DELAY)
    #sendPendingMessages()


