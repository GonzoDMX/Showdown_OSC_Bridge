"""

Config file contains global variables

"""
import wx
import threading

''' Locks for thread safe accessing of variables '''
dict_lock = threading.Lock()
input_lock = threading.Lock()
start_lock = threading.Lock()
end_lock = threading.Lock()
recvd_lock = threading.Lock()

''' Sets the UDP Server Address Values '''
input_ip =  "127.0.0.101" # Defines the UDP Server input IP Addr
input_port = "9001"     # Defines the UDP Server input port
device_count = 0        # Set number of available output devices



''' Thread safe access to input ip and port'''
def getInputAddress():
    global input_lock
    input_lock.acquire()
    global input_ip
    global input_port
    addr = input_ip
    port = input_port
    input_lock.release()
    return addr, port

def setInputAddress(addr, port):
    global input_lock
    input_lock.acquire()
    global input_ip
    global input_port
    input_ip = addr
    input_port = port
    input_lock.release()
    return

''' Flags for managing thread process '''
thread_server = threading.Thread()
server_start = False
end_thread = False      # Sets Flag to close UDP Server thread

def getServerStart():
    global start_lock
    start_lock.acquire()
    global server_start
    val = server_start
    start_lock.release()
    return val

def setServerStart(val):
    global start_lock
    start_lock.acquire()
    global server_start
    server_start = val
    start_lock.release()
    return
    
def getServerEnd():
    global end_lock
    end_lock.acquire()
    global end_thread
    val = end_thread
    end_lock.release()
    return val

def setServerEnd(val):
    global end_lock
    end_lock.acquire()
    global end_thread
    end_thread = val
    end_lock.release()
    return

''' Sets all input and device variables and is syncronized with JSON '''
config_dictionary = {"input": {}, "device": {}}

def setDictInputs(addr, port):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    config_dictionary["input"]["address"] = addr
    config_dictionary["input"]["port"] = port
    dict_lock.release()
    return

def getDictDevices():
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    dev = config_dictionary["device"]
    dict_lock.release()
    return dev

def getDictDevKeys():
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    temp = []
    for key in config_dictionary["device"]:
        temp.append(key)
    dict_lock.release()
    return temp

def getDictNotLinked(exclude):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    temp = []
    for key in config_dictionary["device"]:
        try:
            if key not in exclude:
                if config_dictionary["device"][key]["linked"] == "":
                    temp.append(key)
        except KeyError:
            temp.append(key)
    dict_lock.release()
    return temp


def addDevice(name, link, addr, port):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    config_dictionary["device"][name] = {"id": device_count, "address": addr, "port": port, "linked_to": link, "linked": "" }
    if link != "":
        config_dictionary["device"][link]["linked"] = name
    dict_lock.release()
    return
    
def updateDevice(name, link_to, old_link_to, addr, port):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    dev_id = config_dictionary["device"][name]["id"]
    link = config_dictionary["device"][name]["linked"]
    config_dictionary["device"][name] = {"id": dev_id, "address": addr, "port": port, "linked_to": link_to, "linked":link }
    if link_to != old_link_to:
        if link_to != "":
            config_dictionary["device"][link_to]["linked"] = name
        if old_link_to != "":
            config_dictionary["device"][old_link_to]["linked"] = ""
    dict_lock.release()
    return

def getDeviceId(name):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    i = config_dictionary["device"][name]["id"]
    dict_lock.release()
    return i

def getDeviceLinkedTo(name):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    link_to = config_dictionary["device"][name]["linked_to"]
    dict_lock.release()
    return link_to

def getDeviceLink(name):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    link = config_dictionary["device"][name]["linked"]
    dict_lock.release()
    return link

def getDeviceAddress(name):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    addr = config_dictionary["device"][name]["address"]
    port = config_dictionary["device"][name]["port"]
    dict_lock.release()
    return addr, port

def delDevice(name):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    link_to = config_dictionary["device"][name]["linked_to"]
    if link_to != "":
        config_dictionary["device"][link_to]["linked"] = ""
    link = config_dictionary["device"][name]["linked"]
    if link != "":
        config_dictionary["device"][link]["linked_to"] = ""
    del config_dictionary["device"][name]["id"]
    del config_dictionary["device"][name]["address"]
    del config_dictionary["device"][name]["port"]
    del config_dictionary["device"][name]["linked"]
    del config_dictionary["device"][name]["linked_to"]
    del config_dictionary["device"][name]
    dict_lock.release()
    return
    
def reorderDevice(val):
    global dict_lock
    dict_lock.acquire()
    global config_dictionary
    for dev in config_dictionary["device"]:
        if config_dictionary["device"][dev]["id"] > val:
            config_dictionary["device"][dev]["id"] -= 1
    dict_lock.release()
    return

''' Variables for managing the Device Create/Edit dialog'''
dialog_mode = False     # Sets Dialog mode True = Add, False = Edit
dialog_name = ""        # Stores Device Name
dialog_link_to = ""        # Stores Link Reference Name / Key
dialog_addr = ""        # Stores Device Address
dialog_port = ""        # Stores Device Port

''' Variable to flag recvd messages on a device '''
recvd_on = list()              # Indexes the device that receivedd a message
recvd_off = list()          # Lowers flag of a recvd device

def getRecOnList():
    global recvd_lock
    recvd_lock.acquire()
    global recvd_on
    l = recvd_on
    recvd_lock.release()
    return l

def appendRecOnList(index):
    global recvd_lock
    recvd_lock.acquire()
    global recvd_on
    recvd_on.append(index)
    recvd_lock.release()
    return

''' Set Custom dialog IDs '''
ID_ENGLISH = wx.NewId()
ID_FRANCAIS = wx.NewId()

