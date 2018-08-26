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
from NetworkGlobalDefinitions import *


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
                print (e)
                LOGPRINT(str(self.address) + " socket error: " + str(e))
                LOGPRINT("Closing socket" + str(self.address))
                del openConnections[self.peerName]
                return

            if (len(incommingMessage)):
                LOGPRINT(self.peerName + " >> Msg received: " + str(incommingMessage))
                response = self.handleIncommingMessage(str(incommingMessage))
                self.connectionSocket.sendall(response.encode('utf-8'))


    def startHeatbeatThread(self, connection):
        '''
        Starts a heartbeat thread with the connection to tell the other party we're still alive
        '''
        self.heartBeatRunning = True
        while True:
            connection.sendall(HEARBEAT_MESSAGE.encode('utf-8'))
            sleep(HEARBEAT_INTERVAL)


    def handleIncommingMessage(self, incommingMessage):
        '''
        Handle incomming messages
        '''
        try:
            messageDict = parseIncomingMessage(incommingMessage)
        except Exception as e:
            LOGPRINT("Error parsing incoming message: " + str(e))
            return("ERROR")

        
        if (incommingMessage==UPDATE_COMMAND):
            updateCodebase()
            return KILLING_THREAD

        elif (incommingMessage==KILL_COMMAND):
            return KILLING_THREAD

        return "ACK"

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
    # LOGPRINT("\n\n")
    # LOGPRINT("----------------------------------------------")
    # LOGPRINT("Starting new client")
    # updateLocalMappings()
    # updatePeerMappings(peerMappings)
    # connectToPeers()
    # listenForIncommingConnections()

    messageNum = 4
    message = PeerMessage(messageNum)
    if (message == PeerMessage.HEARBEAT_MESSAGE):
        print("heartbeat")
    if (message == PeerMessage.RETURN_MESSAGE):
        print("return")
    if (message == PeerMessage.UPDATE_PROJECT_COMMAND):
        print("update")
    if (message == PeerMessage.PUSH_PROJECT_COMMAND):
        print("push")
    if (message == PeerMessage.KILL_CLIENT_COMMAND):
        print("kill")


