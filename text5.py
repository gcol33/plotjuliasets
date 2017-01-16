import wx
import matplotlib.pyplot as plt
class Frame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.panel = wx.Panel(self)  ## Makes panel
        self.Bind(wx.EVT_CLOSE, self.closewindow)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.panel.SetSizer(sizer)
        self.Show()

        nameBox = wx.TextEntryDialog(None, 'What is your number?', 'Enter number', '')

        if nameBox.ShowModal() == wx.ID_OK:
        	global value 
        	value = float(nameBox.GetValue())
        	print value

    def closewindow(self, e):
        self.Destroy()


app = wx.App()
frame = Frame(None, 'Print a function ver0.5')
app.MainLoop()

#x = GetNumber(message = 'What is your number?')
print value