"""

Config file contains global variables

"""

import threading

''' Flags for managing thread process '''
end_thread = False      # Sets Flag to close UDP Server thread
restart_thread = False  # Sets flag to restart the UDP Server thread
thread_server = threading.Thread()
thread_count = 0


''' Sets all input and device variables and is syncronized with JSON '''
config_dictionary = {"input": {}, "devices": {}}


''' Sets the UDP Server Address Values '''
input_ip =  "127.0.0.1" # Defines the UDP Server input IP Addr
input_port = "7001"       # Defines the UDP Server input port


''' Variables for managing the Device Create/Edit dialog'''
dialog_mode = False
dialog_name = ""
dialog_addr = ""
dialog_port = ""

