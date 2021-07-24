import re


''' Determine if an incoiming message is valid '''
''' Example of properly formatted message DeviceName(/hog/playback/go/0, 1) '''
def verifyMessage(text):
    #simple = "^([A-Za-z0-9_ ]+)\( *([/a-zA-Z0-9]+), *(\[[\D\d]*\]|[0-9]+\.[0-9]+|[0-9]+|\"[\D\d]+\")\)$"
    simple = "(?i)^([A-Za-z0-9_ ]+)\( *([/a-zA-Z0-9]+), *(\[[\D\d]*\]|[0-9]+\.[0-9]+|[0-9]+|\"[\D\d]+\")(?:,\ *(true|false))?\)$"
    try:
        parsedMessage = re.findall(simple, text)[0]
        if len(parsedMessage) == 3 or len(parsedMessage) == 4:
            return parsedMessage
        else:
            return 0
    except Exception as e:
        return 0



''' Parse incoming UDP Messages and return tuple of values '''
def parseIncoming(text):
    elems = verifyMessage(text)
    if not elems:
        return 0
    else:
        oscName = elems[0]   # Get the device name
        oscAddr = elems[1]      # Get the Osc Parameter Address String
        args = elems[2]
        # Parse Arguments here
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
        # Get linked flag
        linked = True
        if len(elems) == 4:
            if elems[3].lower() == "false":
                linked = False
        return (oscName, oscAddr, oscArgs, linked)
        
        
        
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



def CheckIP(addr, index):
    iCount = len(addr)
    addr = re.sub(r"[^0-9.,]", '', addr)
    if len(addr) < iCount:
        index -= 1
    addr = addr.replace(',', '.')
    ''' Check how many points there are '''
    p = addr.count('.')
    if p > 3:       # If there are too many remove the last
        addr = addr[:index-1] + addr[index:]
        index -= 1

    return addr, index
    
    
