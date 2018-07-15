'''
Dynamitelaw

Contains a collection of useful utility functions.
'''

import sys
import time
import datetime
from datetime import timedelta, date


def printLocation(text="$VER: Locate_Demo.py_Version_0.00.10_(C)2007-2012_B.Walker_G0LCU.", x=0, y=0):
    '''
    I found this arcane shit on stackOverflow. DO NOT TOUCH IT!

    Allows you to print in a specific location in the terminal.
    NOTE Only works in linux
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
    Date must be passed as an string in the following format: "YYYY-MM-DD"
    '''
    year, month, day = dateSplitter(date)

    tempdate = datetime.date(year, month, day) 
    day = tempdate.strftime("%A")
    if ((day == "Sunday") or (day == "Saturday")):
        return False
    else:
        return True


def daterange(start_date, end_date):
    '''
    Provides an iterable over specified date range.
    Dates are strings in the format "YYYY-MM-DD"
    '''
    startDateList = start_date.split("-")
    endDateList = end_date.split("-")
    startDate = date(int(startDateList[0]), int(startDateList[1]), int(startDateList[2]))
    endDate = date(int(endDateList[0]), int(endDateList[1]), int(endDateList[2]))

    for n in range(int ((endDate - startDate).days)):
        yield (startDate + timedelta(n)).strftime("%Y-%m-%d")


def dateSplitter(date):
    '''
    Returns a tuple of ints (year, month, day)
    '''
    dateList = date.split("-")
    year = int(dateList[0])
    month = int(dateList[1])
    day = int(dateList[2])

    return year, month, day

def dateParser(date_string):
    '''
    Returns a datetime date object for the date string of the form YYYY-MM-DD
    '''
    output_date = date(*dateSplitter(date_string))
    output_date = datetime.datetime.combine(output_date,datetime.time(0,0))
    return output_date

def getDayDifference(startDate, endDate):
    '''
    Returns a date object. Date must be a string "YYYY-MM-DD"
    '''
    startYear, startMonth, startDay = dateSplitter(startDate)
    endYear, endMonth, endDay = dateSplitter(endDate)
    
    dayDifference = int( (date(endYear, endMonth, endDay) - date(startYear, startMonth, startDay)).days)
    return dayDifference


def compareDates(date_A, date_B):
    '''
    Returns -1 if A < B, 0 if A = B, and 1 if A > B.
    Date must be a string "YYYY-MM-DD".
    '''
    A = dateSplitter(date_A)
    B = dateSplitter(date_B)

    if (B[0] > A[0]):
        return -1
    if (B[1] > A[1]):
        return -1
    if (B[2] > A[2]):
        return -1

    if (A[0] > B[0]):
        return -1
    if (A[1] > B[1]):
        return -1
    if (A[2] > B[2]):
        return -1
    
    return 0


def estimateYearlyGrowth(startValue, endValue, daysRun, frequencyPerYear=12):
    '''
    Returns the approximate yearly growth rate.
    Solved for r in compound interest formula, defualts to compounding monthly
    '''
    return (frequencyPerYear * ((endValue/startValue)**(30.4375/daysRun))) - frequencyPerYear


def floor(valueIn, floor=0):
    '''
    Returns the floor if the value in is less than the floor, 
    else returns the valueIn
    '''
    if (valueIn > floor):
        return valueIn
    else:
        return floor


def printProgressBar(completed, total):
    '''
    Prints the percent completed out of the total
    '''
    percentage = int(float(completed*1000)/(total-1))/10.0
    sys.stdout.write("\r")
    sys.stdout.write(str(percentage)+"%")
    sys.stdout.flush()
