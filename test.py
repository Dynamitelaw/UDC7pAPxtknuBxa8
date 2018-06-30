import multiprocessing
from multiprocessing import Process
import sys
import utils
from utils import printLocation
import time
#from ctypes import *
from PandaDatabase import database

def test(number):
    x = number + 1
    sys.stdout.write(str(x))
    sys.stdout.write("\r")
    sys.stdout.flush()

def main():
    numbers = [5,7,9]
    for n in numbers:
        p = Process(target=test, args=(n,))
        p.start()

def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')

# This function is just basic for this DEMO but shows the power of the ANSI _Esc_ codes...
def locate(user_string="$VER: Locate_Demo.py_Version_0.00.10_(C)2007-2012_B.Walker_G0LCU.", x=0, y=0):
	# Don't allow any user errors. Python's own error detection will check for
	# syntax and concatination, etc, etc, errors.
	x=int(x)
	y=int(y)
	if x>=255: x=255
	if y>=255: y=255
	if x<=0: x=0
	if y<=0: y=0
	HORIZ=str(x)
	VERT=str(y)
	# Plot the user_string at the starting at position HORIZ, VERT...
	print("\033["+VERT+";"+HORIZ+"f"+user_string)



if __name__ == '__main__':
    d = database()
    #input("Block")
    #print(d.getDataframe("ELDO"))
    #print(d.getDataframe("JoseRubianes"))
    #print_at(6, 3, "Hello")

    frame = d.getDataframe("EKSO")
    f = frame.loc[frame.index < 20140307, ["Open","2 Day Slope"]]
    print(frame)
    print(f)
    #frame.at["2000-08-03", "Open"] = 42
    #d.saveDataframe("ELDO", frame)
    