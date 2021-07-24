import wx
import re
import socket

import config as c
from data_helpers import CheckIP

class DeviceDialog(wx.Dialog): 
    def __init__(self, parent, title): 
        super(DeviceDialog, self).__init__(parent, title = title, size = (270,185)) 
        panel = wx.Panel(self)
        
        self.error = 0  # Input Error flag
        
        self.link_choices = ["Not Linked"]
        if not c.dialog_mode:
            if c.dialog_link_to:
                self.link_choices.append(c.dialog_link_to)
            self.link_choices.extend(c.getDictNotLinked([c.dialog_name, c.getDeviceLink(c.dialog_name)]))
        else:
            self.link_choices.extend(c.getDictNotLinked([""]))
        
        ''' Create device name entry fields '''
        self.label_NAME = wx.StaticText(panel, label='Device Name:', pos=(10, 13))
        if c.dialog_mode:
            self.text_NAME = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(90, 10))
        else:
            self.text_NAME = wx.TextCtrl(panel, style=wx.TE_READONLY, size=(145,22), pos=(90,10))
        self.text_NAME.Bind(wx.EVT_TEXT, self.set_name)
        self.text_NAME.Bind(wx.EVT_SET_FOCUS, self.focus_name)

        ''' Allow Linking device '''
        self.label_LINK = wx.StaticText(panel, label='Link Device: ', pos=(10,38))
        self.combo_LINK = wx.ComboBox(panel, choices=self.link_choices, style=wx.CB_READONLY, size=(145,22), pos=(90, 35))
        self.combo_LINK.Bind(wx.EVT_COMBOBOX, self.set_link)


        ''' Create the device address entry field '''
        self.label_IP_ADDR = wx.StaticText(panel, label='IP Address:', pos=(10, 63))
        self.text_IP_ADDR = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(90, 60))
        self.text_IP_ADDR.Bind(wx.EVT_TEXT, self.set_ipaddr)
        self.text_IP_ADDR.Bind(wx.EVT_SET_FOCUS, self.focus_addr)
        self.text_IP_ADDR.SetMaxLength(15)
        
        
        ''' Create the device port entry field'''
        self.label_PORT = wx.StaticText(panel, label='Input PORT:', pos=(10, 88))
        self.text_PORT = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(90, 85))
        self.text_PORT.Bind(wx.EVT_TEXT, self.set_port)
        self.text_PORT.Bind(wx.EVT_SET_FOCUS, self.focus_port)

        self.combo_LINK.SetSelection(0)
        
        ''' If dialog is opened in edit mode set fields '''
        if not c.dialog_mode:
            self.text_NAME.SetValue(c.dialog_name)
            self.text_IP_ADDR.SetValue(c.dialog_addr)
            self.text_PORT.SetValue(c.dialog_port)
            if c.dialog_link_to:
                self.combo_LINK.SetValue(c.dialog_link_to)
            
        
        if len(self.link_choices) == 1:
            self.combo_LINK.Disable()
        
        ''' Create the ok and cancel operation buttons '''
        self.button_OK = wx.Button(panel, wx.ID_OK, label = "Okay", size = (50,20), pos = (70,120))
        self.button_OK.Bind(wx.EVT_BUTTON, self.okay_button)
        self.button_CANCEL = wx.Button(panel, wx.ID_CANCEL, label = "Cancel", size = (50,20), pos = (135,120))
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
        
        
    ''' Set the OSC  Device Link '''
    def set_link(self, e):
        link = self.combo_LINK.GetStringSelection()
        if link == "Not Linked":
            c.dialog_link_to = ""
        else:
            c.dialog_link_to = link
            
        
    ''' Set the OSC Device IP Address '''
    def set_ipaddr(self, e):
        addr = self.text_IP_ADDR.Value
        index = self.text_IP_ADDR.GetInsertionPoint()
        addr, index = CheckIP(addr, index)
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
            if c.dialog_name in c.config_dictionary["device"]:
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