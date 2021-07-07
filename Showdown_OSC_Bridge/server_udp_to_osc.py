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
	server_udp_to_osc.py contains a class for building the UDP server
	and OSC clients that form the core functionality of Showdown OSC

"""

import wx
import socket
from pythonosc import udp_client

import config as c
from data_helpers import parseIncoming

class UDP_To_OSC_Server(object):
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        
        in_addr, in_port =c.getInputAddress()               # Thread lock input_ip, input_port
        wx.LogStatus("Starting Showdown Server @ " + 
                    in_addr + ":" + str(in_port))           
        
        ''' Set max size of incoming messages '''
        self.buffer_size = 1024
        
        ''' Returns a list of available devices '''
        self.devices = c.getDictDevices()                   # Thread lock config_dictionary
        self.devList = self.getDevList(self.devices)
        
        ''' If there are no available devices close thread'''        
        if len(self.devList) == 0:
            wx.LogStatus("No available OSC outputs found")
            wx.LogStatus("Server startup aborted")
            self.closeThread(False)
        else:
            ''' Open UDP Server Socket '''
            self.sock = self.openSocket(in_addr, in_port)
            ''' Check if successful '''
            if self.sock == 0:
                wx.LogStatus("Error: Failed to open socket")
                self.closeThread(False)
            else:
                c.setServerStart(True)                        # Thread lock server_start
                wx.LogStatus("Showdown Server Online!")
                while c.getServerEnd() == False:              # Thread lock end_thread
                    try:
                        bytesPair = self.sock.recvfrom(self.buffer_size)
                        mess = bytesPair[0].decode("utf-8").replace('\n', '').replace('\r', '')
                        addr = bytesPair[1]
                        wx.LogStatus("Received:\t " + addr[0] + ":" + str(addr[1]) + 
                                     " -> \'" + mess + "\'")
                        result = parseIncoming(mess)
                        if result != 0:
                            try:
                                ''' Get index of target device '''                                
                                index = self.devices[result[0]]["id"]-1
                                self.devList[index][1].send_message(result[1], result[2])
                                c.appendRecOnList(index)    # Thread lock recvd_on 
                                wx.LogStatus("Sending:\t " + result[0] + " -> " + "\'" +
                                            result[1] + "\'" + "  args{ " + str(result[2]) 
                                            + " }" )
                                
                            except KeyError:
                                wx.LogStatus('Error: \"' + result[0] + '\" does not exist')
                        else:
                            wx.LogStatus("Error: Invalid message received")
                    except socket.timeout:
                        continue
                    except OSError:
                        self.closeThread(True)
                        break
                
                self.closeThread(True)
                
            
    ''' Get the Output Devices and create a list of (key, client Interface) pairs '''
    def getDevList(self, devices):
        devList = list()
        for key in devices:
            client = udp_client.SimpleUDPClient(devices[key]["address"], int(devices[key]["port"]))
            devList += [(key, client)]
        return devList
            
    
    ''' Open a UDP Socket '''        
    def openSocket(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((ip, int(port)))
            sock.setblocking(0)
            sock.settimeout(1.0)
            return sock
        except OSError:
            return 0
        
    
    ''' If theres a problem wait here for App to close thread '''
    def closeThread(self, flag):
        if flag:
            wx.LogStatus("Closing Showdown Server")
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        c.restart_thread = True
        
