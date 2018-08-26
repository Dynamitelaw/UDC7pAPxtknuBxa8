'''
Dynamitelaw

Utility functions for the Distributed Network module
'''

import datetime
import time
import socket
import threading

logPrintLock = threading.Lock()

def LOGPRINT(messsage):
    '''
    Add the message to the log file
    '''
    print(messsage)

    logPath = "DistributedNetworking/Logs/MsgLog.txt"
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    logPrintLock.acquire()
    with open(logPath, "a") as myfile:
        myfile.write(socket.gethostname() + " " + timestamp + " >> " + str(messsage) + "\n")
        myfile.close()
    logPrintLock.release()