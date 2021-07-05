import wx
import re
import socket

import config as c

class DeviceDialog(wx.Dialog): 
    def __init__(self, parent, title): 
        super(DeviceDialog, self).__init__(parent, title = title, size = (270,160)) 
        panel = wx.Panel(self)
        
        self.error = 0  # Input Error flag
        
        ''' Create device name entry fields '''
        self.Label_NAME = wx.StaticText(panel, label='Device Name:', pos=(10, 13))
        if c.dialog_mode:
            self.text_NAME = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(90, 10))
        else:
            self.text_NAME = wx.TextCtrl(panel, style=wx.TE_READONLY, size=(145,22), pos=(90,10))
        self.text_NAME.Bind(wx.EVT_TEXT, self.set_name)
        self.text_NAME.Bind(wx.EVT_SET_FOCUS, self.focus_name)

        ''' Create the device address entry field '''
        self.label_IP_ADDR = wx.StaticText(panel, label='IP Address:', pos=(10, 38))
        self.text_IP_ADDR = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(90, 35))
        self.text_IP_ADDR.Bind(wx.EVT_TEXT, self.set_ipaddr)
        self.text_IP_ADDR.Bind(wx.EVT_SET_FOCUS, self.focus_addr)

        ''' Creat the device port entry field'''
        self.label_PORT = wx.StaticText(panel, label='Input PORT:', pos=(10, 63))
        self.text_PORT = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(90, 60))
        self.text_PORT.Bind(wx.EVT_TEXT, self.set_port)
        self.text_PORT.Bind(wx.EVT_SET_FOCUS, self.focus_port)
        
        ''' If dialog is opened in edit mode set fields '''
        if not c.dialog_mode:
            self.text_NAME.SetValue(c.dialog_name)
            self.text_IP_ADDR.SetValue(c.dialog_addr)
            self.text_PORT.SetValue(c.dialog_port)
        
        ''' Create the ok and cancel operation buttons '''
        self.button_OK = wx.Button(panel, wx.ID_OK, label = "Okay", size = (50,20), pos = (70,95))
        self.button_OK.Bind(wx.EVT_BUTTON, self.okay_button)
        self.button_CANCEL = wx.Button(panel, wx.ID_CANCEL, label = "Cancel", size = (50,20), pos = (135,95))
        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.cancel_button)
        
        
    ''' Used to clear an error signal '''
    def focus_name(self, e):
        if self.error == 1:
            self.text_NAME.SetBackgroundColour(wx.Colour(255,255,255))
            self.Refresh()
            self.error = 0
        e.Skip()
    def focus_addr(self, e):
        if self.error == 2:
            self.text_IP_ADDR.SetBackgroundColour(wx.Colour(255,255,255))
            self.Refresh()
            self.error = 0
        e.Skip()
    def focus_port(self, e):
        if self.error == 3:
            self.text_PORT.SetBackgroundColour(wx.Colour(255,255,255))
            self.Refresh()
            self.error = 0
        e.Skip()
    
    ''' Set the OSC Device Name '''
    def set_name(self, e):
        name = self.text_NAME.Value
        val = re.findall("[a-zA-Z0-9\ \_]", name)
        name = ""
        for vals in val:
            name += vals
        c.dialog_name = name
        index = self.text_NAME.GetInsertionPoint()
        self.text_NAME.ChangeValue(name) # Set value w/o triggering event
        self.text_NAME.SetInsertionPoint(index)  # Reset the inmsertion point to end
        
    
    ''' Set the OSC Device IP Address '''
    def set_ipaddr(self, e):
        addr = self.text_IP_ADDR.Value
        index = self.text_IP_ADDR.GetInsertionPoint()
        addr = addr.replace("..", ".")
        val = re.findall("\D", addr)
        for vals in val:
            if vals != '.':
                addr = addr.replace(vals, '')
                index -= 1
        val = re.findall("[0-9]+", addr)
        addr = ""
        for count, vals in enumerate(val):
            if vals == "00" or vals == "000":
                vals = "0"
            if len(vals) > 1 and vals[0] == "0":
                vals = vals[1:]
                index -= 1
            while len(vals) > 3 or int(vals) > 255:
                vals = vals[:-1]
            if count == 3:
                addr += vals
                break
            else:
                addr += vals + '.'
        c.dialog_addr = addr
        self.text_IP_ADDR.ChangeValue(addr) # Set value w/o triggering event
        self.text_IP_ADDR.SetInsertionPoint(index)  # Reset the inmsertion point to end
        
        
    ''' Set the OSC Device Port '''
    def set_port(self, e):
        port = self.text_PORT.Value  # Get the textctrl string
        val = re.findall("\D", port)    # Get a list of all invalid characters
        for vals in val:                # If there are any remove them
            port = port.replace(vals, '')
        index = self.text_PORT.GetInsertionPoint()
        if port:
            if int(port) > 65535:       # If over max value block additional nums
                port = port[0 : index-1 : ] + port[index : :]
                index -= 1
        c.dialog_port = port
        self.text_PORT.ChangeValue(port) # Set value w/o triggering event
        self.text_PORT.SetInsertionPoint(index)  # Reset the inmsertion point to end
        
        
    ''' Okay button is pressed, check values, report error or proceed '''
    def okay_button(self, e):
        if c.dialog_mode:
            if c.dialog_name in c.config_dictionary["devices"]:
                self.text_NAME.SetBackgroundColour(wx.Colour(255,0,0))
                self.Refresh()
                self.error = 1
                return
        if c.dialog_name:
            if c.dialog_port:
                try:
                    socket.inet_pton(socket.AF_INET, c.dialog_addr)
                    self.EndModal(wx.ID_OK)
                except socket.error:
                    self.text_IP_ADDR.SetBackgroundColour(wx.Colour(255,0,0))
                    self.Refresh()
                    self.error = 2
            else:
                self.text_PORT.SetBackgroundColour(wx.Colour(255,0,0))
                self.Refresh()
                self.error = 3
        else:
            self.text_NAME.SetBackgroundColour(wx.Colour(255,0,0))
            self.Refresh()
            self.error = 1
            
        
    ''' Cancel the operation '''    
    def cancel_button(self, e):
        self.EndModal(wx.ID_CANCEL)