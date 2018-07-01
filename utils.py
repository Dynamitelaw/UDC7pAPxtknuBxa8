'''
Dynamitelaw

Contains a collection of useful functions that are not integral to
DW functions. 

DO NOT DELETE ANYTHING!
'''

import sys
import time
import datetime

def printLocation(text="$VER: Locate_Demo.py_Version_0.00.10_(C)2007-2012_B.Walker_G0LCU.", x=0, y=0):
    '''
    I found this arcane shit on stackOverflow. DO NOT TOUCH IT!

    Allows you to print in a specific location in the terminal.
    '''
    x=int(x)
    y=int(y)
    if x>=255: x=255
    if y>=255: y=255
    if x<=0: x=0
    if y<=0: y=0
    HORIZ=str(x)
    VERT=str(y)
    # Plot the user_string at the starting at position HORIZ, VERT...
    #print ("\033["+VERT+";"+HORIZ+"f"+text ,)
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()


def splitList(inputList, numberOfChunks):
    '''
    Splits the inputList into the specified number of chunks (roughly equal size).
    '''
    seperatingIndexes = []
    lenghtOfInputList = len(inputList)
    chunkSize = int(lenghtOfInputList/numberOfChunks)

    for i in range(0, numberOfChunks, 1):
        if (i==0):
            seperatingIndexes.append([0,chunkSize])
        elif (i == (numberOfChunks-1)):
            seperatingIndexes.append([seperatingIndexes[i-1][1], lenghtOfInputList])
        else:
            seperatingIndexes.append([seperatingIndexes[i-1][1], ((i+1)*chunkSize)])

    outputList = []
    for indexes in seperatingIndexes:
        outputList.append(inputList[indexes[0]:indexes[1]])

    return outputList


def emitAsciiBell():
    '''
    Prints the ASCII bell character, telling the system to emit it's standard bell sound.
    '''
    print("\a\r")
    time.sleep(1)


def sanitizeString(stringToSanitize):
    disallowedCharacters = ["/", ".", "\\", "$"]
    
    for char in disallowedCharacters:
        stringToSanitize = stringToSanitize.replace(char, "")

    return stringToSanitize        


def convertDate(dateInteger, outputFormat="List"):
    '''
    Insert comment here
    '''
    day = str(dateInteger)[-2:]
    month = str(dateInteger)[-4:-2]
    year = str(dateInteger)[:-4]

    if (outputFormat=="List"):
        return int(year), int(month), int(day)
    if (outputFormat=="String"):
        return str(year)+"-"+str(month)+"-"+str(day)


def extractTicker(dict):
    '''
    Returns the value associated with the key "symbol" in the passed dictionary.
    Sounds pointless, but this function vastly improves the efficiency
    of extracting ticker symbols.
    '''
    return dict.get('symbol')


def isWeekday(date):
    '''
    Returns a bool: True if weekday, False if weekend.
    Date must be passed as an int in the following format: YYYYMMDD
    '''
    year, month, day = convertDate(date)

    tempdate = datetime.date(year, month, day) 
    day = tempdate.strftime("%A")
    if ((day == "Sunday") or (day == "Saturday")):
        return False
    else:
        return True
