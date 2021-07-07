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

	config.py contains global variables for use
	across different modules in Showdown OSC

"""

import wx
import threading

''' Locks for thread safe accessing of variables '''
dict_lock = threading.Lock()
input_lock = threading.Lock()
dcount_lock = threading.Lock()
start_lock = threading.Lock()
end_lock = threading.Lock()
recvd_lock = threading.Lock()

''' Sets the UDP Server Address Values '''
input_ip =  "127.0.0.101" # Defines the UDP Server input IP Addr
input_port = "7001"     # Defines the UDP Server input port
device_count = 0        # Set number of available output devices



''' Thread safe access to input ip and port'''
def getInputAddress():
    input_lock.acquire()
    global input_ip
    global input_port
    addr = input_ip
    port = input_port
    input_lock.release()
    return addr, port

def setInputAddress(addr, port):
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
    start_lock.acquire()
    global server_start
    val = server_start
    start_lock.release()
    return val

def setServerStart(val):
    start_lock.acquire()
    global server_start
    server_start = val
    start_lock.release()
    return
    
def getServerEnd():
    end_lock.acquire()
    global end_thread
    val = end_thread
    end_lock.release()
    return val

def setServerEnd(val):
    end_lock.acquire()
    global end_thread
    end_thread = val
    end_lock.release()
    return

''' Sets all input and device variables and is syncronized with JSON '''
config_dictionary = {"input": {}, "devices": {}}

def setDictInputs(addr, port):
    dict_lock.acquire()
    global config_dictionary
    config_dictionary["input"]["address"] = addr
    config_dictionary["input"]["port"] = port
    dict_lock.release()
    return

def getDictDevices():
    dict_lock.acquire()
    global config_dictionary
    dev = config_dictionary["devices"]
    dict_lock.release()
    return dev

def addDevice(name, addr, port):
    dict_lock.acquire()
    global config_dictionary
    config_dictionary["devices"][name] = {"id": device_count, "address": addr, "port": port }
    dict_lock.release()
    return
    
def updateDevice(name, addr, port):
    dict_lock.acquire()
    global config_dictionary
    config_dictionary["devices"][name] = {"address": addr, "port": port }
    dict_lock.release()
    return

def getDeviceId(name):
    dict_lock.acquire()
    global config_dictionary
    i = config_dictionary["devices"][name]["id"]
    dict_lock.release()
    return i

def getDeviceAddress(name):
    dict_lock.acquire()
    global config_dictionary
    addr = config_dictionary["devices"][name]["address"]
    port = config_dictionary["devices"][name]["port"]
    dict_lock.release()
    return addr, port

def delDevice(name):
    dict_lock.acquire()
    global config_dictionary
    del config_dictionary["devices"][name]["id"]
    del config_dictionary["devices"][name]["address"]
    del config_dictionary["devices"][name]["port"]
    del config_dictionary["devices"][name]
    dict_lock.release()
    return
    
def reorderDevice(val):
    dict_lock.acquire()
    global config_dictionary
    for dev in config_dictionary["devices"]:
        if config_dictionary["devices"][dev]["id"] > val:
            config_dictionary["devices"][dev]["id"] -= 1
    dict_lock.release()
    return

''' Variables for managing the Device Create/Edit dialog'''
dialog_mode = False     # Sets Dialog mode True = Add, False = Edit
dialog_name = ""        # Stores Device Name
dialog_addr = ""        # Stores Device Address
dialog_port = ""        # Stores Device Port

''' Variable to flag recvd messages on a device '''
recvd_on = list()              # Indexes the device that receivedd a message
recvd_off = list()          # Lowers flag of a recvd device

def getRecOnList():
    recvd_lock.acquire()
    global recvd_on
    l = recvd_on
    recvd_lock.release()
    return l

def appendRecOnList(index):
    recvd_lock.acquire()
    global recvd_on
    recvd_on.append(index)
    recvd_lock.release()
    return

''' Set Custom dialog IDs '''
ID_ENGLISH = wx.NewId()
ID_FRANCAIS = wx.NewId()

