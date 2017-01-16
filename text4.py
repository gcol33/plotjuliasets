import wx

class Frame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(-1, -1))
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.btn = wx.Button(self.panel, -1, "Name-a-matic")
        self.Bind(wx.EVT_BUTTON, self.GetNumber, self.btn)
        #self.txt = wx.TextCtrl(self.panel, -1, size=(140,-1))
        #self.txt.SetValue('name goes here')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.btn)
        #sizer.Add(self.txt)

        self.panel.SetSizer(sizer)
        self.Show()

    def GetNumber(self, message='', default_value=''):

        dlg = wx.TextEntryDialog(self.panel, message='', defaultValue=default_value)
        dlg.ShowModal()
        #self.txt.SetValue(dlg.GetValue())
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def OnCloseWindow(self, e):
        self.Destroy()

app = wx.App()
frame = Frame(None, 'My Nameomatic')
app.MainLoop()

#x = GetNumber(message = 'What is your number?')
