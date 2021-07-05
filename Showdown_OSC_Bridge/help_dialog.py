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
