import wx
import socket
import data_helpers
from datetime import datetime
from pythonosc import udp_client

import config as c
from data_helpers import parseIncoming
from _datetime import date


class UDP_To_OSC_Server(object):
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        
        ''' Set max size of incoming messages '''
        self.buffer_size = 1024
        
        self.tCount = c.thread_count
        
        ''' Returns a list of available devices '''
        self.devList = self.getDevList()
        
        ''' If there are no available devices close thread'''        
        if len(self.devList) == 0:
            self.closeThread(False)
        else:
            wx.LogStatus("Starting Showdown Server @ " + 
                         c.input_ip + ":" + str(c.input_port))
            ''' Open UDP Server Socket '''
            self.sock = self.openSocket()
            ''' Check if successful '''
            if self.sock == 0:
                wx.LogStatus("Error: Failed to open socket")
                self.closeThread(False)
            else:
                wx.LogStatus("Showdown Server Online!")
                while c.end_thread == False:
                    try:
                        bytesPair = self.sock.recvfrom(self.buffer_size)
                        mess = bytesPair[0].decode("utf-8")
                        addr = bytesPair[1]
                        wx.LogStatus("Received from " + addr[0] + ":" + str(addr[1]) + " -> \'" + mess + "\'")
                        result = parseIncoming(mess)
                        if result != 0:
                            try:
                                ''' Get index of target device '''
                                for count, device in enumerate(self.devList):
                                    if result[0] == device[0]:
                                        index = count
                                        break
                                ''' Send OSC Message '''
                                self.devList[index][1].send_message(result[1], result[2])
                                wx.LogStatus("Sending to " + result[0] + " -> " + "\'" +
                                             result[1] + "\'" + "  args{ " + str(result[2]) + " }" )
                            except UnboundLocalError:
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
    def getDevList(self):
        devDict = c.config_dictionary["devices"]
        devList = list()
        for key in devDict:
            client = udp_client.SimpleUDPClient(devDict[key]["address"], int(devDict[key]["port"]))
            devList += [(key, client)]
        return devList
            
    
    ''' Open a UDP Socket '''        
    def openSocket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((c.input_ip, int(c.input_port)))
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
        
