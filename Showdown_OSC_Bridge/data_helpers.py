import re


''' Determine if an incoiming message is valid '''
''' Example of properly formatted message DeviceName(/hog/playback/go/0, 1) '''
def verifyMessage(text):
    pattern = "^([A-Za-z0-9_]+)\( *([/a-zA-Z0-9]+), *(\[{1}(?: ?(?:[0-9]+\.?[0-9]*){1},{1})*(?: ?[0-9]+\.?[0-9]*)\]{1}|(?:[0-9]+\.?[0-9]*))\)$"
    try:
        x = re.findall(pattern, text)[0]
        if len(x) == 3:
            return x
        else:
            return 0
    except Exception as e:
        print("Error: " + str(e))
        return 0



''' Parse incoming UDP Messages and return tuple of values '''
def parseIncoming(text):
    #text = bMessage.decode("utf-8")
    elems = verifyMessage(text)
    if not elems:
        print("Message received is not properly formatted")
        return 0
    else:
        oscName = elems[0]   # Get the device name
        oscAddr = elems[1]      # Get the Osc Parameter Address String
        if '[' in elems[2]:     # If the argument is an array
            pattern = "[0-9]+\.?[0-9]*"
            xArg = re.findall(pattern, elems[2])
            oscArgs = list()
            for vals in xArg:
                oscArgs.append(strIntFloat(vals))  # Create list from the array argument
        else:
            oscArgs = strIntFloat(elems[2]) # Return argument as Int or FLoat
        return (oscName, oscAddr, oscArgs)
        
        
        
""" Receive a value represented as a string and convert to float or int """        
def strIntFloat(x):
    if '.' in x:
        return float(x)   # Gets argument if it is a float
    else:
        return int(x) # Gets argument if it is an integer
        
