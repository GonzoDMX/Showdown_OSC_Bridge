"""

Config file contains global variables

"""
import wx
import threading

''' Flags for managing thread process '''
end_thread = False      # Sets Flag to close UDP Server thread
restart_thread = False  # Sets flag to restart the UDP Server thread
thread_server = threading.Thread()
thread_count = 0
server_start = False

''' Sets all input and device variables and is syncronized with JSON '''
config_dictionary = {"input": {}, "devices": {}}

''' Sets the UDP Server Address Values '''
input_ip =  "127.0.0.1" # Defines the UDP Server input IP Addr
input_port = "7001"     # Defines the UDP Server input port

''' Variables for managing the Device Create/Edit dialog'''
dialog_mode = False     # Sets Dialog mode True = Add, False = Edit
dialog_name = ""        # Stores Device Name
dialog_addr = ""        # Stores Device Address
dialog_port = ""        # Stores Device Port

''' Variable to flag recvd messages on a device '''
recvd_on = -1              # Indexes the device that receivedd a message
recvd_off = -1          # Lowers flag of a recvd device

''' Set Custom dialog IDs '''
ID_ENGLISH = wx.NewId()
ID_FRANCAIS = wx.NewId()