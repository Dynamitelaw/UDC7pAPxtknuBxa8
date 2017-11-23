'''
Dynamitelaw

Contains a collection of useful functions that are not integral to
DW functions. 

DO NOT DELETE ANYTHING!
'''

import sys

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
    print "\033["+VERT+";"+HORIZ+"f"+text ,
    sys.stdout.flush()