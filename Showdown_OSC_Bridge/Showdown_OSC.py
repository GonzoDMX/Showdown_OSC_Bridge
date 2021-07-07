#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Showdown OSC
    Created by: Andrew O'Shei, andrewoshei.com
    Date: July 5, 2021
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

"""
	Showdown_OSC.py contains the main program loop and a
	class for constructiong the main GUI in Showdown OSC
	
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
from config import getRecOnList


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
        
        
        ''' Create Input IP Address input field '''
        self.Label_IN_ADDR = wx.StaticText(pnl, label='Input IP Address:', pos=(10, 13))
        self.text_IN_ADDR = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(110, 10))
        self.text_IN_ADDR.Bind(wx.EVT_TEXT, self.validate_in_ipaddr)
        self.text_IN_ADDR.Bind(wx.EVT_SET_FOCUS, self.focus_addr)
        
        ''' Create Input Port input field '''
        self.label_IN_PORT = wx.StaticText(pnl, label='Input Port:', pos=(10, 38))
        self.text_IN_PORT = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER, size=(145, 22), pos=(110, 35))
        self.text_IN_PORT.Bind(wx.EVT_TEXT, self.validate_in_port)
        self.text_IN_PORT.Bind(wx.EVT_SET_FOCUS, self.focus_port)

        ''' Displays the Server Status '''
        self.text_STATUS = wx.TextCtrl(pnl, style=wx.TE_CENTRE,size=(60,22), pos=(265,10))
        self.text_STATUS.Bind(wx.EVT_SET_FOCUS, self.focus_status)
        self.text_STATUS.SetBackgroundColour(wx.Colour(255,0,0))
        self.text_STATUS.SetForegroundColour(wx.Colour(255,255,255))
        self.text_STATUS.SetValue("Offline")

        ''' Create button for asserting changes to the input address '''
        self.button_SET = wx.Button(pnl, label='Set Input', size=(60,22), pos=(265, 35))
        self.button_SET.Bind(wx.EVT_BUTTON, self.set_input_address)
        self.button_SET.Disable()

        ''' Create the List Widget for displaying and selecting OSC Devices '''
        self.box_OUT = wx.StaticBox(pnl, label="Output Devices:", size=(325,265), pos=(5, 65))
        self.list_DEVICES = wx.ListCtrl(pnl, name='OSC Devices', style=wx.LC_REPORT|wx.LC_HRULES|wx.BORDER_SIMPLE|wx.LC_SINGLE_SEL, pos=(10, 85), size=(315, 200))
        self.list_DEVICES.Bind(wx.EVT_LIST_ITEM_SELECTED, self.set_select)
        self.list_DEVICES.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.set_select)
        self.list_DEVICES.AppendColumn("OSC Device", format=wx.LIST_FORMAT_LEFT, width=130)
        self.list_DEVICES.AppendColumn("IP Address", format=wx.LIST_FORMAT_LEFT, width=100)
        self.list_DEVICES.AppendColumn("Port", format=wx.LIST_FORMAT_LEFT, width=50)
        self.list_DEVICES.AppendColumn("Rx", format=wx.LIST_FORMAT_CENTER, width=30)

        ''' Create Buttons to Add, Edit and Remove OSC Devices '''
        self.button_ADD = wx.Button(pnl, label='Add', pos=(10, 295))
        self.button_ADD.Bind(wx.EVT_BUTTON, self.add_osc_device)
        self.button_REMOVE = wx.Button(pnl, label='Remove', pos=(125, 295))
        self.button_REMOVE.Bind(wx.EVT_BUTTON, self.remove_osc_device)
        self.button_EDIT = wx.Button(pnl, label='Edit', pos=(238, 295))
        self.button_EDIT.Bind(wx.EVT_BUTTON, self.edit_osc_device)

        self.button_REMOVE.Disable()
        self.button_EDIT.Disable()


        ''' Create Utility buttons'''
        self.button_DONER = wx.Button(pnl, label='Donate', pos=(10, 335))
        self.button_DONER.Bind(wx.EVT_BUTTON, self.please_donate)
        self.button_HELP = wx.Button(pnl, label='Help', pos=(125, 335))
        self.button_HELP.Bind(wx.EVT_BUTTON, self.get_help)
        
        ''' Create button for opening message logger '''
        self.button_LOG = wx.Button(pnl, label='Log', pos=(238, 335))
        self.button_LOG.Bind(wx.EVT_BUTTON, self.get_logger)
        
        ''' Create App watermark '''
        self.static_credit = wx.StaticText(pnl, label=Disclaimer1, pos=(45, 370))
        self.static_message = wx.StaticText(pnl, label=Disclaimer2, pos=(35, 385))
        
        ''' Set main frame size and params '''
        self.SetSize((350, 450))
        self.SetMinSize((350, 450))
        self.SetMaxSize((350, 450))
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
                for count, key in enumerate(c.config_dictionary["devices"]):
                    self.list_DEVICES.InsertItem(count, key)
                    self.list_DEVICES.SetItem(count, 1, c.config_dictionary["devices"][key]["address"])
                    self.list_DEVICES.SetItem(count, 2, c.config_dictionary["devices"][key]["port"])
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
            self.list_DEVICES.SetItem(c.recvd_off.pop(), 3, "")
        ''' Turn flag off '''
        while r_on:
            i = r_on.pop()
            self.list_DEVICES.SetItem(i, 3, "●")
            c.recvd_off.append(i)
        return
        
                
    ''' Wipes device list and repopulates '''
    def update_device_list(self):
        self.list_DEVICES.DeleteAllItems()
        devDict = c.getDictDevices()
        for count, key in enumerate(devDict):
            self.list_DEVICES.InsertItem(count, key)
            self.list_DEVICES.SetItem(count, 1, devDict[key]["address"])
            self.list_DEVICES.SetItem(count, 2, devDict[key]["port"])


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
                name = self.list_DEVICES.GetItemText(index)
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
                        for dev in c.config_dictionary["devices"]:
                            if c.config_dictionary["devices"][dev]["id"] > del_id:
                                c.config_dictionary["devices"][dev]["id"] -= 1
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
                name = self.list_DEVICES.GetItemText(index)
                c.dialog_name = name
                c.dialog_addr, c.dialog_port = c.getDeviceAddress(name)
                with DeviceDialog(self, "Edit OSC Device") as dialog:
                    if dialog.ShowModal() == wx.ID_OK:
                        self.update_device_dict()
                        self.update_device_list()
                        wx.LogStatus("Edited device: " + c.dialog_name + "/" + 
                             c.dialog_addr + ":" + c.dialog_port)
                        c.setServerEnd(True)
        self.button_REMOVE.Disable()
        self.button_EDIT.Disable()


    ''' Add new device to dictionary '''
    def add_device_dict(self):
        c.device_count += 1
        c.addDevice(c.dialog_name, c.dialog_addr, c.dialog_port)
        self.save_device_dict()

    ''' Edit new device to dictionary '''
    def update_device_dict(self):
        c.updateDevice(c.dialog_name, c.dialog_addr, c.dialog_port)
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
        
