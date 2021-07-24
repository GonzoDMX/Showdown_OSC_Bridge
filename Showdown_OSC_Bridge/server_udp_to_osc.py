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
                wx.LogStatus("Error: \t Failed to open socket")
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
                            name = result[0]
                            log_flag = "Sending:"
                            try:
                                while True:
                                    ''' Get index of target device '''
                                    index = self.devices[name]["id"]-1
                                    self.devList[index][1].send_message(result[1], result[2])
                                    c.appendRecOnList(index)    # Thread lock recvd_on 
                                    wx.LogStatus(log_flag + "\t " + name + " -> " + "\'" +
                                                result[1] + "\'" + "  args{ " + str(result[2])
                                                + " }" )
                                    if result[3]:
                                        name = self.devices[name]["linked"]
                                        log_flag = "Linking:"
                                        if not name:
                                            break
                                    else:
                                        wx.LogStatus("Info:\t Link Override")
                                        break
                            except KeyError:
                                wx.LogStatus('Error: \t \"' + name + '\" does not exist')
                        else:
                            wx.LogStatus("Error: \t Invalid message received")
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
        