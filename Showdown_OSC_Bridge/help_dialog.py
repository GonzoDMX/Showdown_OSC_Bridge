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
	help_dialog.py contains a class for building the language
	select dialog for displaying help documents in Showdown OSC

"""

import wx
import config as c

class HelpDialog(wx.Dialog): 
    def __init__(self, parent, title): 
        super(HelpDialog, self).__init__(parent, title = title, size = (255,120)) 
        panel = wx.Panel(self)
        
        text = "Select language for help document.\nSelectionnez la langue pour le document."
        
        ''' Create device name entry fields '''
        self.Label_NAME = wx.StaticText(panel, label=text, pos=(10, 13))

        ''' Create the lang select buttons '''
        self.button_EN = wx.Button(panel, c.ID_ENGLISH, label = "English", pos = (23,50))
        self.button_EN.Bind(wx.EVT_BUTTON, self.on_button)
        self.button_FR = wx.Button(panel, c.ID_FRANCAIS, label = "Francais", pos = (125,50))
        self.button_FR.Bind(wx.EVT_BUTTON, self.on_button)
        
        
    def on_button(self, e):
        if self.IsModal():
            self.EndModal(e.EventObject.Id)
        else:
            self.Close()
