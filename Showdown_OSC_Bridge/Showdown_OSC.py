#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Showdown OSC Bridge
    Created by: Andrew O'Shei, andrewoshei.com
    Date: July 4, 2021

"""

import wx
import socket
import json
import re
import sys
import os
import threading
import webbrowser

import config as c

from dialog_device import DeviceDialog
from help_dialog import HelpDialog
from server_udp_to_osc import UDP_To_OSC_Server
from data_helpers import CheckIP


Disclaimer1 = "Created by: Andrew O\'Shei, andrewoshei.com"
Disclaimer2 = "If you find this program useful consider donating"

donate_url = "https://www.paypal.com/donate?hosted_button_id=KYC95YV7JQSS2"

icon_path = "./WO_Icon1.ico"
help_file_en = "Showdown_OSC_Bridge_Help_EN.pdf"
help_file_fr = "Showdown_OSC_Bridge_Help_FR.pdf"
data_path = "./device_data.json"

""" Class contains the main App Logic """
class BuildGUI(wx.Frame):
    def __init__(self, *args, **kw):
        super(BuildGUI, self).__init__(*args, **kw)
        
        ''' Set up timer for managing the Server Thread '''
        self.thread_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.thread_manager, self.thread_timer)
        self.thread_timer.Start(1000)
        
        ''' Set up timer for managing message received flags '''
        self.recvd_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.flag_recvd, self.recvd_timer)
        self.recvd_timer.Start(150)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.InitGUI()
        
    ''' Build the Graphic Interface '''    
    def InitGUI(self):
        pnl = wx.Panel(self)

        self.error = 0
        
        self.log_window = wx.LogWindow(self, "Showdown Log", False)
        
        hbox = wx.BoxSizer(wx.VERTICAL)
        
        inbox = wx.StaticBoxSizer(wx.HORIZONTAL, pnl, "Input Configuration:")
        
        fgs_INPUT = wx.FlexGridSizer(2,3,5,5)
        
        ''' Create Input IP Address input field '''
        self.label_IN_ADDR = wx.StaticText(pnl, label='Input IP Address:')
        self.text_IN_ADDR = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER, size=(145, 22))
        self.text_IN_ADDR.Bind(wx.EVT_TEXT, self.validate_in_ipaddr)
        self.text_IN_ADDR.Bind(wx.EVT_SET_FOCUS, self.focus_addr)
        
        ''' Create Input Port input field '''
        self.label_IN_PORT = wx.StaticText(pnl, label='Input Port:')
        self.text_IN_PORT = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER, size=(145, 22))
        self.text_IN_PORT.Bind(wx.EVT_TEXT, self.validate_in_port)
        self.text_IN_PORT.Bind(wx.EVT_SET_FOCUS, self.focus_port)

        ''' Displays the Server Status '''
        self.text_STATUS = wx.TextCtrl(pnl, style=wx.TE_CENTRE,size=(60,22))
        self.text_STATUS.Bind(wx.EVT_SET_FOCUS, self.focus_status)
        self.text_STATUS.SetBackgroundColour(wx.Colour(255,0,0))
        self.text_STATUS.SetForegroundColour(wx.Colour(255,255,255))
        self.text_STATUS.SetValue("Offline")

        ''' Create button for asserting changes to the input address '''
        self.button_SET = wx.Button(pnl, label='Set Input', size=(60,22))
        self.button_SET.Bind(wx.EVT_BUTTON, self.set_input_address)
        self.button_SET.Disable()

        
        fgs_INPUT.AddMany([(self.label_IN_ADDR, 1, wx.EXPAND), 
                           (self.text_IN_ADDR, 1, wx.EXPAND), 
                           (self.text_STATUS, 1, wx.EXPAND), 
                           (self.label_IN_PORT, 1, wx.EXPAND), 
                           (self.text_IN_PORT, 1, wx.EXPAND), 
                           (self.button_SET, 1, wx.EXPAND)])

        fgs_INPUT.AddGrowableCol(1, 1)

        inbox.Add(fgs_INPUT, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)

        sbox = wx.StaticBoxSizer(wx.VERTICAL, pnl, "Output Devices:")

        ''' Create the List Widget for displaying and selecting OSC Devices '''
        self.list_DEVICES = wx.ListCtrl(pnl, name='OSC Devices', style=wx.LC_REPORT|wx.LC_HRULES|wx.BORDER_SIMPLE|wx.LC_SINGLE_SEL)
        self.list_DEVICES.Bind(wx.EVT_LIST_ITEM_SELECTED, self.set_select)
        self.list_DEVICES.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.set_select)
        self.list_DEVICES.AppendColumn("ID", format=wx.LIST_FORMAT_LEFT, width=30)
        self.list_DEVICES.AppendColumn("OSC Device", format=wx.LIST_FORMAT_LEFT, width=130)
        self.list_DEVICES.AppendColumn("Link", format=wx.LIST_FORMAT_LEFT, width=40)
        self.list_DEVICES.AppendColumn("IP Address", format=wx.LIST_FORMAT_LEFT, width=100)
        self.list_DEVICES.AppendColumn("Port", format=wx.LIST_FORMAT_LEFT, width=50)
        self.list_DEVICES.AppendColumn("Rx", format=wx.LIST_FORMAT_CENTER, width=30)

        fgs_BUTT1 = wx.FlexGridSizer(1, 3, 5, 5)

        ''' Create Buttons to Add, Edit and Remove OSC Devices '''
        self.button_ADD = wx.Button(pnl, label='Add', size=(50, 30))
        self.button_ADD.Bind(wx.EVT_BUTTON, self.add_osc_device)
        self.button_REMOVE = wx.Button(pnl, label='Remove', size=(50, 30))
        self.button_REMOVE.Bind(wx.EVT_BUTTON, self.remove_osc_device)
        self.button_EDIT = wx.Button(pnl, label='Edit', size=(50, 30))
        self.button_EDIT.Bind(wx.EVT_BUTTON, self.edit_osc_device)

        self.button_REMOVE.Disable()
        self.button_EDIT.Disable()

        fgs_BUTT1.AddMany([(self.button_ADD, 1, wx.EXPAND), 
                           (self.button_REMOVE, 1, wx.EXPAND), 
                           (self.button_EDIT, 1, wx.EXPAND)])
        
        fgs_BUTT1.AddGrowableCol(0, 1)
        fgs_BUTT1.AddGrowableCol(1, 1)
        fgs_BUTT1.AddGrowableCol(2, 1)
        
        
        sbox.Add(self.list_DEVICES, proportion=5, flag=wx.ALL|wx.EXPAND, border=5)
        sbox.Add(fgs_BUTT1, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        
        fgs_BUTT2 = wx.FlexGridSizer(1, 3, 5, 5)

        ''' Create Utility buttons'''
        self.button_DONER = wx.Button(pnl, label='Donate', size=(50, 30))
        self.button_DONER.Bind(wx.EVT_BUTTON, self.please_donate)
        self.button_HELP = wx.Button(pnl, label='Help', size=(50, 30))
        self.button_HELP.Bind(wx.EVT_BUTTON, self.get_help)
        
        ''' Create button for opening message logger '''
        self.button_LOG = wx.Button(pnl, label='Log', size=(50, 30))
        self.button_LOG.Bind(wx.EVT_BUTTON, self.get_logger)
        
        fgs_BUTT2.AddMany([(self.button_DONER, 1, wx.EXPAND), 
                           (self.button_HELP, 1, wx.EXPAND), 
                           (self.button_LOG, 1, wx.EXPAND)])
        
        fgs_BUTT2.AddGrowableCol(0, 1)
        fgs_BUTT2.AddGrowableCol(1, 1)
        fgs_BUTT2.AddGrowableCol(2, 1)
        
        bbox.Add(10, 0, 0)
        bbox.Add(fgs_BUTT2, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        bbox.Add(10, 0, 0)
        
        cbox = wx.BoxSizer(wx.VERTICAL)
        
        ''' Create App watermark '''
        credit1 = wx.StaticText(pnl, label=Disclaimer1, style=wx.ALIGN_CENTER)
        credit2 = wx.StaticText(pnl, label=Disclaimer2, style=wx.ALIGN_CENTER)
        
        cbox.Add(credit1, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        cbox.Add(credit2, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        
        
        hbox.Add(inbox, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        hbox.Add(sbox, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        hbox.Add(bbox, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        hbox.Add(cbox, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        pnl.SetSizer(hbox)
        
        ''' Set main frame size and params '''
        self.SetSize((430, 495))
        self.SetMinSize((430, 495))
        self.SetTitle('Showdown OSC Bridge')
        self.Centre()
        self.Show(True)
        self.populate_devices()


    ''' Populates Device dictionary and ListCtrl '''
    def populate_devices(self):
        try:
            with open(data_path) as json_file:
                c.config_dictionary = json.load(json_file)
                json_file.close()
                c.input_ip = c.config_dictionary["input"]["address"]
                c.input_port = c.config_dictionary["input"]["port"]
                self.text_IN_ADDR.SetValue(c.input_ip)
                self.text_IN_PORT.SetValue(c.input_port)
                for count, key in enumerate(c.config_dictionary["device"]):
                    link_to = c.config_dictionary["device"][key]["linked_to"]
                    self.list_DEVICES.InsertItem(count, str(c.config_dictionary["device"][key]["id"]))
                    self.list_DEVICES.SetItem(count, 1, key)
                    try:
                        if link_to:
                            self.list_DEVICES.SetItem(count, 2, str(c.config_dictionary["device"][link_to]["id"]))
                        else:
                            self.list_DEVICES.SetItem(count, 2, "")
                    # For backwards compatibility
                    except KeyError:
                        self.list_DEVICES.SetItem(count, 2, "")
                    self.list_DEVICES.SetItem(count, 3, c.config_dictionary["device"][key]["address"])
                    self.list_DEVICES.SetItem(count, 4, c.config_dictionary["device"][key]["port"])
                    c.device_count += 1
                c.thread_server = Launch_Server_Thread()
        except Exception as e:
            wx.LogStatus("device_data.json not found")
            c.config_dictionary["input"]["address"] = c.input_ip
            c.config_dictionary["input"]["port"] = c.input_port
            self.text_IN_ADDR.SetValue(c.input_ip)
            self.text_IN_PORT.SetValue(c.input_port)
            wx.LogStatus("Writing device_data.json...")
            try:
                self.save_device_dict()
                wx.LogStatus("Success!")
            except Exception as e:
                wx.LogStatus("Failed!\t" + str(e))


    ''' Releases error signal on text inputs '''
    def focus_addr(self, e):
        if self.error == 1:
            in_addr, _ = c.getInputAddress()
            self.text_IN_ADDR.SetValue(in_addr)
            self.text_IN_ADDR.SetBackgroundColour(wx.Colour(255,255,255))
            self.Refresh()
            self.error = 0
        e.Skip()
    def focus_port(self, e):
        if self.error == 2:
            _, in_port = c.getInputAddress()
            self.text_IN_PORT.SetValue(in_port)
            self.text_IN_PORT.SetBackgroundColour(wx.Colour(255,255,255))
            self.Refresh()
            self.error = 0
        e.Skip()

    ''' Rejects selection of status textctrl '''
    def focus_status(self, e):
        self.Label_IN_ADDR.SetFocus() # Diverts focus to static text object
        return

    ''' Manages starting and restarting the Server Thread '''
    def thread_manager(self, *args, **kwargs):
        if c.getServerStart():
            self.text_STATUS.SetBackgroundColour(wx.Colour(0,200,0))
            self.text_STATUS.SetForegroundColour(wx.Colour(255,255,255))
            c.setServerStart(False)
            self.text_STATUS.SetValue("Online")
        if c.getServerEnd():
            if not c.thread_server.is_alive():
                self.text_STATUS.SetBackgroundColour(wx.Colour(255,0,0))
                self.text_STATUS.SetForegroundColour(wx.Colour(255,255,255))
                self.text_STATUS.SetValue("Offline")
                c.setServerEnd(False)
                c.thread_server = Launch_Server_Thread()
        return


    ''' Creates a visual marker when a specific devices has received a message '''
    def flag_recvd(self, e):
        r_on = c.getRecOnList()
        ''' Turn flag on '''
        while c.recvd_off:
            self.list_DEVICES.SetItem(c.recvd_off.pop(), 5, "")
        ''' Turn flag off '''
        while r_on:
            i = r_on.pop()
            self.list_DEVICES.SetItem(i, 5, "●")
            c.recvd_off.append(i)
        return
        
                
    ''' Wipes device list and repopulates '''
    def update_device_list(self):
        self.list_DEVICES.DeleteAllItems()
        devDict = c.getDictDevices()
        for count, key in enumerate(devDict):
            link_to = c.config_dictionary["device"][key]["linked_to"]
            self.list_DEVICES.InsertItem(count, str(c.config_dictionary["device"][key]["id"]))
            self.list_DEVICES.SetItem(count, 1, key)
            try:
                if link_to:
                    self.list_DEVICES.SetItem(count, 2, str(c.config_dictionary["device"][link_to]["id"]))
                else:
                    self.list_DEVICES.SetItem(count, 2, "")
            # For backwards compatibility
            except KeyError:
                self.list_DEVICES.SetItem(count, 2, "")
            self.list_DEVICES.SetItem(count, 3, devDict[key]["address"])
            self.list_DEVICES.SetItem(count, 4, devDict[key]["port"])


    ''' Validates IP Address value is valid'''
    def validate_in_ipaddr(self, e):
        addr = self.text_IN_ADDR.Value
        index = self.text_IN_ADDR.GetInsertionPoint()
        addr, index = CheckIP(addr, index)
        self.text_IN_ADDR.ChangeValue(addr)         # Set value w/o triggering event
        self.text_IN_ADDR.SetInsertionPoint(index)  # Reset the inmsertion point to end
        in_addr, _ = c.getInputAddress()
        if addr != in_addr:
            self.button_SET.Enable()
        else:
            self.button_SET.Disable()


    ''' Validates Port Value is valid '''
    def validate_in_port(self, e):
        port = self.text_IN_PORT.Value              # Get the textctrl string
        val = re.findall("\D", port)                # Get a list of all invalid characters
        for vals in val:                            # If there are any remove them
            port = port.replace(vals, '')
        index = self.text_IN_PORT.GetInsertionPoint()
        if port:
            if int(port) > 65535:                   # If over max value block additional nums
                port = port[0 : index-1 : ] + port[index : :]
                index -= 1
        self.text_IN_PORT.ChangeValue(port)         # Set value w/o triggering event
        self.text_IN_PORT.SetInsertionPoint(index)  # Reset the inmsertion point to end
        _, in_port = c.getInputAddress()
        if port != in_port:
            self.button_SET.Enable()
        else:
            self.button_SET.Disable()
            

    """ Set a new IP Address and Port """
    def set_input_address(self, e):
        addr = self.text_IN_ADDR.Value
        port = self.text_IN_PORT.Value
        if port:
            try:
                socket.inet_pton(socket.AF_INET, addr)
                c.setDictInputs(addr, port)
                c.setInputAddress(addr, port)
                self.save_device_dict()
                self.button_SET.Disable()
                c.setServerEnd(True)
            except socket.error:
                self.text_IN_ADDR.SetBackgroundColour(wx.Colour(255,0,0))
                self.Refresh()
                self.error = 1
        else:
            self.text_IN_PORT.SetBackgroundColour(wx.Colour(255,0,0))
            self.Refresh()
            self.error = 2


    ''' If item is selected or deselected toggle Remove and Edit buttons'''
    def set_select(self, e):
        item = self.list_DEVICES.GetFocusedItem()
        if item != -1 and self.list_DEVICES.IsSelected(item):
            self.button_REMOVE.Enable()
            self.button_EDIT.Enable()
        else:
            self.button_REMOVE.Disable()
            self.button_EDIT.Disable()


    """ Opens a dialog for adding an OSC Device """
    def add_osc_device(self, e):
        c.dialog_mode = True
        c.dialog_link_to = ""
        with DeviceDialog(self, "Add OSC Device") as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.add_device_dict()
                self.update_device_list()
                c.setServerEnd(True)
                wx.LogStatus("New device added: " + c.dialog_name + "/" + 
                             c.dialog_addr + ":" + c.dialog_port)


    """ Opens a dialog for editing an OSC Device """
    def remove_osc_device(self, e):
        index = self.list_DEVICES.GetFocusedItem()
        if index > -1:
            if self.list_DEVICES.IsSelected(index):
                name = self.list_DEVICES.GetItemText(index, 1)
                dialog_remove = wx.MessageDialog(
                    None,
                    'Remove device \"' + name + '\" ?',
                    "Remove Output Device",
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING
                    ).ShowModal()
                if dialog_remove == wx.ID_YES:
                    del_id = c.getDeviceId(name)
                    c.delDevice(name)
                    if del_id < c.device_count:
                        c.reorderDevice(del_id)
                        for dev in c.config_dictionary["device"]:
                            if c.config_dictionary["device"][dev]["id"] > del_id:
                                c.config_dictionary["device"][dev]["id"] -= 1
                    c.device_count -= 1
                    self.save_device_dict()
                    self.update_device_list()
                    wx.LogStatus("Device removed: " + name)
                    c.setServerEnd(True)
                else:
                    return
        self.button_REMOVE.Disable()
        self.button_EDIT.Disable()

        
    """ Opens a dialog for editing an OSC Device """
    def edit_osc_device(self, e):
        c.dialog_mode = False
        ''' Get the selected device '''
        index = self.list_DEVICES.GetFocusedItem()
        if index > -1:
            if self.list_DEVICES.IsSelected(index):
                name = self.list_DEVICES.GetItemText(index, 1)
                old_link_to = c.getDeviceLinkedTo(name)
                c.dialog_name = name
                c.dialog_link_to = old_link_to
                c.dialog_addr, c.dialog_port = c.getDeviceAddress(name)
                with DeviceDialog(self, "Edit OSC Device") as dialog:
                    if dialog.ShowModal() == wx.ID_OK:
                        self.update_device_dict(old_link_to)
                        self.update_device_list()
                        wx.LogStatus("Edited device: " + c.dialog_name + "/" + 
                             c.dialog_addr + ":" + c.dialog_port)
                        if c.dialog_link_to:
                            wx.LogStatus("Device Linked to: " + c.dialog_link_to)
                        c.setServerEnd(True)
        self.button_REMOVE.Disable()
        self.button_EDIT.Disable()


    ''' Add new device to dictionary '''
    def add_device_dict(self):
        c.device_count += 1
        c.addDevice(c.dialog_name, c.dialog_link_to, c.dialog_addr, c.dialog_port)
        self.save_device_dict()

    ''' Edit new device to dictionary '''
    def update_device_dict(self, old_link_to):
        c.updateDevice(c.dialog_name, c.dialog_link_to, old_link_to, c.dialog_addr, c.dialog_port)
        self.save_device_dict()
        
        
    ''' Saves device dict to JSON '''
    def save_device_dict(self):
        with open(data_path, 'w') as json_file:
            json.dump(c.config_dictionary, json_file)
            json_file.close()

    def get_logger(self, e):
        self.log_window.Show()


    ''' Redirects to paypal donation '''
    def please_donate(self, e):
        webbrowser.open( donate_url, new=2)

    ''' Displays app user manual '''
    def get_help(self, e):
        with HelpDialog(self, "Help") as dialog:
            dialog_id = dialog.ShowModal()
            if dialog_id == c.ID_ENGLISH:
                os.startfile(help_file_en)
            if dialog_id == c.ID_FRANCAIS:
                os.startfile(help_file_fr)

        
        
    ''' Triggers on close app event '''
    def on_close(self, event):
        Quit_Program()
        


''' Launch UDP Server as a thread '''
def Launch_Server_Thread():
    Thread = threading.Thread(target=UDP_To_OSC_Server)
    Thread.start()
    return Thread
        

''' Executes on quitting the program '''
def Quit_Program():
    c.end_thread = True
    sys.exit()
    
    
def main():
    ex = wx.App()
    BuildGUI(None)
    wx.Log.SetTimestamp("%H:%M:%S ")
    wx.LogStatus("Showdown OSC Bridge")
    ex.MainLoop()

if __name__ == '__main__':
    main()
        
