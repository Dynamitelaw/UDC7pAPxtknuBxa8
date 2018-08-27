'''
Dynamitelaw

Send commands to peers on the mesh network
'''

#External Imports
from random import randint

#Custom Imports
import SystemPathImports
from NetworkDefinitions import *
from DistributionUtils import createCommandMessages, LOGPRINT
from DistributedFunctions import openNewClietWindow


class SubscriptionHandler():
    '''
    Class responsible for handling subscription return values
    '''
    #If you want your command to be subscribable, you need to add a handler function here <COMENTFLAG=ADDING_NEW_BOT_FUNCTIONALITY>

    def __init__(self, subscriptionID, messageType):
        self.id = subscriptionID
        self.messageType = messageType

    def handleReturnMessage(self, returnDict):
        '''
        Handle the return values of this subscription
        '''
        if (self.messageType == PEER_MESSAGE.GENERIC_MESSAGE):
            #print(returnDict)
            pass
        elif (self.messageType == PEER_MESSAGE.INSTALL_PACKAGES_COMMAND):
            self.handleInstallPackageReturn(returnDict)

        #Unhandled message type
        else:
            raise ValueError("Message type " + str(self.messageType.value) + "not handled by subscription handler")

    #--------------------
    # Handler functions
    #--------------------
    def handleInstallPackageReturn(self, returnDict):
        LOGPRINT("Peer has finished installing packages. Here are the results...")
        LOGPRINT("Overall Success = " + str(returnDict["CommandSucess"]))

        packageResults = returnDict["ReturnValues"]
        for result in packageResults:
            LOGPRINT("\t" + str(result))

    # End SubscriptionHandler class
#====================================


def addNewPeerCommand(command=False, commandArguments=False, subscribeToResults=False, commandTargets=[IP_ALL_STR], Subscriptions=False, PendingOutbound=False):
    '''
    Add a new peer command to Subscriptions and/or PendingOutbound.
    All commands are added to PendingOutbound, but are only added to Subscriptions if the command results are subscribed to.
    '''
    #Check for valid inputs
    validInputs = True
    if (command == False):
        validInputs = False
    if (Subscriptions == False):
        validInputs = False
    if (PendingOutbound == False):
        validInputs = False

    if (not validInputs):
        raise ValueError("Missing minimum required arguments. command, Subscription, and PendingOutbound are mandatory")

    #Generate IDs
    subscriptionID = False
    if (subscribeToResults):
        subscriptionID = randint(1, MAX_SUBSCRIPTION_ID)
    broadcastID = randint(1, MAX_BROADCAST_ID)

    #Create JSON messages
    commandMessages = createCommandMessages(command, commandArguments=commandArguments, subscriptionID=subscriptionID, broadcastID=broadcastID, targets=commandTargets)

    #Add messages to PendingOutbound list
    PendingOutbound += commandMessages

    #Subscribe if specified
    if (subscribeToResults):
        handler = SubscriptionHandler(subscriptionID, command)
        Subscriptions[subscriptionID] = handler


def setSubscritptionsAndPendingOutbounds(Subscriptions, PendingOutbound):
    '''
    Populate Subscriptions dictionary and PendingOutbound list with commands to send to peers in the network.
    If you want to send commands to the mesh network, this is where you would put them.
    <COMENTFLAG=ADDING_NEW_BOT_FUNCTIONALITY>
    '''
    #############
    # Example, don't delete me

    # Tell peers to update or install packages (iexfinance and tensorfow)
    # We want to know which packages were successful or not, so we'll subscribe to get the results of our command
    # Since we didn't specify a target, this command will apply to ALL peers in the network
    addNewPeerCommand(command=PEER_MESSAGE.INSTALL_PACKAGES_COMMAND, commandArguments=["iexfinance", "tensorflow"], subscribeToResults=True, Subscriptions=Subscriptions, PendingOutbound=PendingOutbound)

    # Tell two specific peers (IP = 123.45.67.89 and IP = 231.54.76.98) to clear out their log folders. This will happen AFTER they update their packages
    # This command does not generate any return values, so there's no need to subscribe to the results
    # This command also does not require input arguments, so we can ommit those
    addNewPeerCommand(command=PEER_MESSAGE.CLEAR_LOGS_COMMAND, commandTargets=["123.45.67.89", "231.54.76.98"], Subscriptions=Subscriptions, PendingOutbound=PendingOutbound)
    #############


if __name__ == '__main__':
    #NOTE: Want to add a new peer command? Search your workspace for "<COMENTFLAG=ADDING_NEW_BOT_FUNCTIONALITY>" to find out where you need to add things

    # To execute the peer commands, this file will kill the program and restart via BotConnection.py
    # BotConnection will call setSubscritptionsAndPendingOutbounds, then send out the peer commands
    openNewClietWindow()
