'''
Dynamitelaw
'''

#External Imports
import socket
import threading
from time import sleep

#Custom Imports
from DistributionUtils import LOGPRINT
import DistributedFunctions


#Define global variables
HEARBEAT_MESSAGE = "HEARTBEAT"
KILLING_THREAD = "KILLLING_THREAD"

UPDATE_COMMAND = "UPDATE PROJECT"

JOEY_IP = "108.35.27.76"
COLE_IP = ""
RAMIN_IP = ""

listenPort = 23

def startHeatbeatThread(connection):
    '''
    Starts a heartbeat thread with the connection to tell the other party we're still alive
    '''
    while True:
        connection.sendall(HEARBEAT_MESSAGE.encode('utf-8'))
        sleep(10)


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
    Handles a single connection
    '''
    t = threading.Thread(target=startHeatbeatThread,args=(connection,))
    t.start()

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
            print("Ending client process...")
            return

 
def startClient():
    '''
    starts the client's main loop
    '''

    incomingHost = ''
    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    LOGPRINT("TCP socket created")

    #Tries to bind the incoming port
    try:
        listen.bind((incomingHost,listenPort))
        LOGPRINT("Socket bound to port: " + str(listenPort))
    except Exception as e:
        print(e)
        LOGPRINT("Error: " + str(e))
        LOGPRINT("Ending client")
        listen.close()
        return

    listen.listen(5)

    #Listens for incoming connection requests
    while True:
        connection, addr = listen.accept()

        LOGPRINT("Connection established with " + str(addr))
        print("Connection established with " + str(addr))

        #Opens new thread for each client
        bufferSize = 4096
        incommingConnectionThread(connection, bufferSize, addr)
        


if __name__ == '__main__':
    startClient()
    #print(HEARBEAT_MESSAGE)

