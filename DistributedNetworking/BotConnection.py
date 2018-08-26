'''
Dynamitelaw
'''

#External Imports
import socket
import threading
from time import sleep

#Custom Imports
from DistributionUtils import LOGPRINT
from DistributedFunctions import *


#Define global variables
outgoingSocketsLock = threading.Lock()
outgoingSockets = []

HEARBEAT_MESSAGE = "HEARTBEAT"
HEARBEAT_INTERVAL = 10
KILLING_THREAD = "KILLLING_THREAD"

UPDATE_COMMAND = "UPDATE PROJECT"

JOEY_DESKTOP_IP = "108.35.27.76"
JOEY_DESKTOP_HOSTNAME = "DESKTOP-NKDVTB2"
COLE_DESKTOP_IP = ""
COLE_DESKTOP_HOSTNAME = ""
RAMIN_DESKTOP_IP = ""
RAMIN_DESKTOP_HOSTNAME = ""

LOCAL_IP = socket.gethostbyname(socket.gethostname())
PORT_LISTEN = 25700


def startHeatbeatThread(connection):
    '''
    Starts a heartbeat thread with the connection to tell the other party we're still alive
    '''
    while True:
        connection.sendall(HEARBEAT_MESSAGE.encode('utf-8'))
        sleep(HEARBEAT_INTERVAL)


def handleIncommingMessage(incommingMessage):
    '''
    Handle incomming messages
    '''

    if (incommingMessage==UPDATE_COMMAND):
        updateCodebase()
        return "KILL_THREAD"

    return "ACK"


def incommingConnectionThread(connection, bufferSize, addr):
    '''
    Handles a single inbound connection
    '''
    #Start a heartbeat thread for this connection
    heartbeatThread = threading.Thread(target=startHeatbeatThread,args=(connection,))
    heartbeatThread.start()

    while True:
        try:
            incommingMessage = connection.recv(bufferSize)
        except Exception as e:
            print (e)
            LOGPRINT("Socket error: " + str(e))

        LOGPRINT("Msg received: " + str(incommingMessage))
        response = handleIncommingMessage(str(incommingMessage))
        connection.sendall(response.encode('utf-8'))

        if (response == KILLING_THREAD):
            LOGPRINT("Ending client process...")
            return
        

def createOutgoingConnections():
    '''
    Creates outgoing connections to all known peers
    '''
    hostname = socket.gethostname()
    peerList = [JOEY_DESKTOP_IP, COLE_DESKTOP_IP, RAMIN_DESKTOP_IP]

    #Determine which peers to try to connect to. Prevent connecting to yourself
    if (hostname == JOEY_DESKTOP_HOSTNAME):
        LOGPRINT("This is Joey's machine")
        peerList.remove(JOEY_DESKTOP_IP)
    elif (hostname == COLE_DESKTOP_HOSTNAME):
        LOGPRINT("This is Cole's desktop")
        peerList.remove(COLE_DESKTOP_IP)
    elif (hostname == RAMIN_DESKTOP_HOSTNAME):
        LOGPRINT("This is Ramin's machine")
        peerList.remove(RAMIN_DESKTOP_IP)

    peerList = [(i, False) for i in peerList]  #Set connection flags to false

    #Loop until connected to all peers
    while True:
        for i in range(0, len(peerList), 1):
            peer = peerList[i]
            isConnected = peer[1]
            peerIP = peer[0]
            PORT_OUTBOUND = PORT_LISTEN+i+1

            #Establish outbound connection if not already connected
            if (not isConnected):
                outbound = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                while True:
                    try:
                        outbound.bind((LOCAL_IP, 0))
                        break
                    except Exception as e:
                        bindingPort += 1

                #LOGPRINT("Binding outbout socket to " +  peerIP + " to port " + str(PORT_OUTBOUND))

                try:
                    outbound.connect((peerIP,PORT_LISTEN))
                    outgoingSocketsLock.acquire()
                    outgoingSockets.append((outbound, peerIP))  #add this outbount socket to our list
                    outgoingSocketsLock.release()
                    LOGPRINT("Successfully created outbound connection with " + peerIP)
                    peerList[i][1] = True  #Set isConnected flag to true for this peer
                except Exception as e:
                    LOGPRINT("Could not connect to " + peerIP + ". Retrying in 60 seconds")


        #Determine who we've connected to and who we haven't
        falseConnectionFlags = [peer[1] for peer in peerList if (not peer[1])]
        if (len(falseConnectionFlags)):
            sleep(60)
        else:
            #We've connected to all our peers. Break the loop
            break


    
def connectToPeers():
    '''
    Tries to create an outgoing connection to all known peers
    '''
    outgoingConnectionThread = threading.Thread(target=createOutgoingConnections,args=())
    outgoingConnectionThread.start()


def startClient():
    '''
    starts the client's main loop
    '''

    incomingHost = ''
    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    LOGPRINT("TCP socket created")

    #Tries to bind the incoming port
    try:
        listen.bind((incomingHost, PORT_LISTEN))
        LOGPRINT("Inbound socket bound to port: " + str(PORT_LISTEN))
    except Exception as e:
        LOGPRINT("Error: " + str(e))
        LOGPRINT("Ending client")
        listen.close()
        return

    listen.listen(5)

    #Listens for incoming connection requests
    while True:
        connection, addr = listen.accept()

        LOGPRINT("Connection established with " + str(addr))

        #Opens new thread for each client
        bufferSize = 4096
        incommingConnectionThread(connection, bufferSize, addr)


if __name__ == '__main__':
    connectToPeers()
    startClient()
    print (LOCAL_IP)

