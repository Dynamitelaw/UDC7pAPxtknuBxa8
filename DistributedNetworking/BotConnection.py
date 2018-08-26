'''
Dynamitelaw
'''

#External Imports
import socket
import threading
from time import sleep

#Custom Imports
from DistributionUtils import LOGPRINT


def startHeatbeatThread(connection):
    '''
    Starts a heartbeat thread with the connection to tell the other party we're still alive
    '''
    while True:
        heartbeat = "HEARTBEAT\n\r"
        connection.sendall(heartbeat.encode('utf-8'))
        sleep(10)


def handleIncommingMessage(incommingMessage):
    '''
    Handle incomming messages
    '''

    return "handled\n\r"


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

 
def startClient():
    '''
    starts the client's main loop
    '''

    incomingHost = ''
    listenPort = 25700
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

