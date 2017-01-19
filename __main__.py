from js1 import *
from js2 import *
import wx
import os
import sys
from sympy import sympify
from sympy import lambdify
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt


class CanvasFrame(wx.Frame):
    def __init__(self):
        # Initialize the frame  
        wx.Frame.__init__(self, None, -1,
                          'Julia Set Plotter v.12', size=(550, 750))
        
        # Initialize variables of the Class
        self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
        self.js = 0 # Variable to see what we plotted
        self.ax = None 
        self.n = 0 # exponent n to use with the newton iteration
        self.xlims = np.array([-2,2]) # set range to -2,2 on the real axes per default
        self.ylims = np.array([-2,2]) # set range to -2,2 on the complex axes per default
        self.cprec = 100 # set the number of pixels we use to plot to 100 per default
        
        # Setting up the menu.
        filemenu= wx.Menu()
        menuSave = filemenu.Append(wx.ID_SAVE, "&QuickSave\tCtrl+S"," Save pic.png")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"&Exit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


        # Menu Events.
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        # Canvas and Buttons
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []

        self.buttons.append(wx.Button(self, -1, "newton iteration")) #0
        self.buttons.append(wx.Button(self, -1, "enter iteration")) #1
        self.buttons.append(wx.Button(self, -1, "update")) #2
        self.buttons.append(wx.Button(self, -1, "precision")) #3
        self.buttons.append(wx.Button(self, -1, "range")) #4
        
        for i in range(0, len(self.buttons)):
            self.sizer2.Add(self.buttons[i], 1, wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.add_toolbar()
        

        self.SetSizer(self.sizer)
        self.Fit()

        # Bind Buttons
        self.Bind(wx.EVT_BUTTON, self.plot, self.buttons[0])
        self.Bind(wx.EVT_BUTTON, self.user_ip, self.buttons[1])
        self.Bind(wx.EVT_BUTTON, self.update, self.buttons[2])
        self.Bind(wx.EVT_BUTTON, self.NxNy, self.buttons[3])
        self.Bind(wx.EVT_BUTTON, self.xylims, self.buttons[4])
        
        
    # A toobar.
    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()

    # function that plots the julia set with the newton iteration
    def plot(self,event):
        self.ax = self.figure.add_subplot(111)
        self.ax.cla()  
        nBox = wx.TextEntryDialog(None, 'Enter exponent', 'z^n-1=0 | n = ?', '')

        if nBox.ShowModal() == wx.ID_OK:
            value = int(nBox.GetValue())
        if nBox.GetValue() == '':
            self.statusbar.SetStatusText("Error: Enter a number")
            return 
        if value < 1:
            self.statusbar.SetStatusText("Please select a meaningful Number")
            self.OnError()
            return 
        else:
            self.statusbar.SetStatusText("")
            maxit = 50 # number of iterations
            lxy = (len(self.xlims)+len(self.ylims))
            self.n = value
            tol = lxy*1e-4    # toleranz for termination criterium that scales with x and y range
            Nx = self.cprec   # mesh points in x-direction
            Ny = self.cprec   # mesh points in y-direction
            Xm, Ym, Z, levels, i = JS_grids(self.n,tol,maxit,Nx,Ny,self.xlims,self.ylims)
            
            self.ax.contourf(Xm,Ym,Z,cmap=plt.cm.get_cmap('jet',len(levels)-1))
            # Store some values to see if we have to update
            self.cprec0 = self.cprec
            self.xaxes0 = self.ax.get_xlim()
            self.yaxes0 = self.ax.get_ylim()
            # Draw on the canvas
            self.canvas.draw() 
            self.js = 0
            if i == maxit:
                self.statusbar.SetStatusText('Maximal number ('+str(i)+') of iterations reached')
            else:
                self.statusbar.SetStatusText(str(i)+' Iterations needed')  
    
    # function that uses the scipy parser to transform user input into usable function
    def user_ip(self,event):
        ''' plot some Julia Sets '''

        uiBox = wx.TextEntryDialog(None, 'Iteration for complex variable\ntipp: try z^2+const.', 'f(z) = ?', '')

        if uiBox.ShowModal() == wx.ID_OK:
            entry = str(uiBox.GetValue())
            entry = entry.replace("i","j")
            f = sympify(entry)
            fs = f.free_symbols
            # Easy check to see if user input makes sense
            if len(fs) == 0:
                self.statusbar.SetStatusText("Error: Enter a variable")
                return 
            if len(fs) > 1:
                self.statusbar.SetStatusText("Error: Enter exactly one variable")
                return 
            # lambdify the input
            f = lambdify(fs,f)
            global func
            func = f
        if uiBox.GetValue() == '':
            self.statusbar.SetStatusText("Error: Enter a number")
        else:
            self.statusbar.SetStatusText("")
            self.ax = self.figure.add_subplot(111)
            self.ax.cla()
            Nx = self.cprec   # mesh points in x-direction
            Ny = self.cprec   # mesh points in y-direction
            Xm, Ym, Z = JS_gridsui(f,Nx,Ny,self.xlims,self.ylims)
            
            levels = np.array([0,1,2])
            self.ax.contourf(Xm,Ym,Z,levels=levels,colors=('w', 'b'))
            # Store some values to see if we have to update
            self.cprec0 = self.cprec
            self.xaxes0 = self.ax.get_xlim()
            self.yaxes0 = self.ax.get_ylim()
            # Draw on the canvas
            self.canvas.draw() 
            self.js = 1

    # updates our current plot if we use the zoom/change prec
    def update(self,event):
        if  self.ax == None:
            self.statusbar.SetStatusText("Error: No image to update")
        elif  self.js == 0:
            self.statusbar.SetStatusText("")  
                
            xaxes = self.ax.get_xlim()
            yaxes = self.ax.get_ylim()
            # See if there is something to update
            if (xaxes == self.xaxes0 and yaxes == self.yaxes0 and self.cprec0 == self.cprec):
                self.statusbar.SetStatusText("Nothing to update")
                return 
            self.ax.cla()
            xlimsu = np.array(xaxes)
            ylimsu = np.array(yaxes)
            maxit = 50 # number of iterations
            lxy = (len(self.xlims)+len(self.ylims))
            tol = lxy*1e-4 # toleranz for termination criterium
            Nx = self.cprec   # mesh points in x-direction
            Ny = self.cprec   # mesh points in y-direction
            Xm, Ym, Z, levels, i = JS_grids(self.n,tol,maxit,Nx,Ny,xlimsu,ylimsu)
            self.ax.contourf(Xm,Ym,Z, cmap=plt.cm.get_cmap('jet',len(levels)-1))
            # Store some values to see if we have to update
            self.xaxes0 = xaxes
            self.yaxes0 = yaxes
            self.cprec0 = self.cprec
            # Draw on the canvas
            self.canvas.draw()
            if i == maxit:
                self.statusbar.SetStatusText('Maximal number ('+str(i)+') of iterations reached')
            else:
                self.statusbar.SetStatusText(str(i)+' Iterations needed')
        elif  self.js == 1:
            self.statusbar.SetStatusText("")  
            xaxes = self.ax.get_xlim()
            yaxes = self.ax.get_ylim()
            # See if there is something to update
            if (xaxes == self.xaxes0 and yaxes == self.yaxes0 and self.cprec0 == self.cprec):
                self.statusbar.SetStatusText("Nothing to update")
                return 
            self.ax.cla()
            xlimsu = np.array(xaxes)
            ylimsu = np.array(yaxes)
            Nx = self.cprec   # mesh points in x-direction
            Ny = self.cprec   # mesh points in y-direction
            Xm, Ym, Z = JS_gridsui(func,Nx,Ny,xlimsu,ylimsu)
            
            levels = np.array([0,1,2])
            self.ax.contourf(Xm,Ym,Z,levels=levels,colors=('w', 'b'))
            # Store some values to see if we have to update
            self.cpre0 = self.cprec
            self.xaxes0 = xaxes
            self.yaxes0 = yaxes
            # Draw on the canvas
            self.canvas.draw() 

    # function where user can enter number of pixels in x and y direction
    def NxNy(self,event):
        ''' Set precision '''
        self.statusbar.SetStatusText("")
        precBox = wx.TextEntryDialog(None, 'Number of Pixels', 'Enter number', '')

        if precBox.ShowModal() == wx.ID_OK:
            self.cprec = int(precBox.GetValue())
            if self.cprec < 2:
                self.statusbar.SetStatusText("Please select a meaningful Number")
                self.OnError()
                self.cprec = 100

    # set x and y range
    def xylims(self,event):
        self.statusbar.SetStatusText("")
        xlimBox = wx.TextEntryDialog(None, 'x limits (f.e. -2,2)', 'Enter number (delimiter is ,)', '')
        if  xlimBox.ShowModal() == wx.ID_OK:
            x_lims = str(xlimBox.GetValue())
            x_lims = x_lims.split(',')
            xmin = float(x_lims[0])
            xmax = float(x_lims[1])
            self.xlims = np.array([xmin,xmax])
        
            
        ylimBox = wx.TextEntryDialog(None, 'y limits (f.e. -2,2)', 'Enter number (delimiter is ,)', '')
        if ylimBox.ShowModal() == wx.ID_OK:
            y_lims = str(ylimBox.GetValue())
            y_lims = y_lims.split(',')
            ymin = float(y_lims[0])
            ymax = float(y_lims[1])
            self.ylims = np.array([ymin,ymax])
        


    # Displays a dialog for what this program is about
    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A small program \n in wxPython to plot Newton-Juila Sets", "About This Program", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    # Exits the program
    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    # Quick save to pic.png with Crtl+S
    def OnSave(self, event):

        self.figure.savefig('pic.png')
        self.statusbar.SetStatusText("pic.png saved")

    # Display Error message 
    def OnError(self):
        # A message dialog box with an Error message. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "## Error ##", "Please enter a meaningful number", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

# App class
class App(wx.App):
    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame()
        frame.Show(True)
        return True

# Open the widget
app = App(0)
app.MainLoop()