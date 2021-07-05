"""
	Created by: Andrew O'Shei
	Date: July 5, 2021

 	This file is part of Showdown OSC.

    Showdown OSC is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

"""

"""
	data_helpers.py contains utility functions for
	parsing incoming UDP message strings in Showdown OSC

"""

import re

''' Determine if an incoiming message is valid '''
''' Example of properly formatted message DeviceName(/hog/playback/go/0, 1) '''
def verifyMessage(text):
    #pattern = "^([A-Za-z0-9_]+)\( *([/a-zA-Z0-9]+), *(\[(?: ?(?:[0-9]+\.?[0-9]*)|(?:\"[\D\d]*\"),)*(?:(?: ?[0-9]+\.?[0-9]*)|(?:\"[\D\d]*\"))\]|(?:[0-9]+\.?[0-9]*)|(?:\"[\D\d]+\"))\)$"
    simple = "^([A-Za-z0-9_]+)\( *([/a-zA-Z0-9]+), *(\[[\D\d]*\]|[0-9]+\.[0-9]+|[0-9]+|\"[\D\d]+\")\)$"
    try:
        x = re.findall(simple, text)[0]
        if len(x) == 3:
            return x
        else:
            return 0
    except Exception as e:
        return 0



''' Parse incoming UDP Messages and return tuple of values '''
def parseIncoming(text):
    #text = bMessage.decode("utf-8")
    elems = verifyMessage(text)
    if not elems:
        return 0
    else:
        oscName = elems[0]   # Get the device name
        oscAddr = elems[1]      # Get the Osc Parameter Address String
        args = elems[2]
        if args[0] == '[' and args[-1] == ']':     # If the argument is an array
            oscArgs = list()
            args = args[1:-1].split(',')
            for arg in args:
                arg = arg.lstrip().rstrip()
                arg = strIntFloat(arg)
                if arg is not None:
                    oscArgs.append(arg)
        else:
            oscArgs = strIntFloat(args) # Return argument as Int or FLoat
        return (oscName, oscAddr, oscArgs)
        
        
        
""" Receives a string and returns it as its correct type """        
def strIntFloat(x):
    if x[0] == '\"' and x[-1] == '\"':
        return x[1:-1]  # Item is a string return as string
    elif '.' in x:
        return float(x) # Gets argument if it is a float
    elif x.isnumeric():
        return int(x)   # Gets argument if it is an integer
    else:
        return None
        
