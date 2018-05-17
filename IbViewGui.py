import time
import tkinter as tk
from tkinter import ttk

import IbView
import IbViewEnums
import IbViewClasses
import IbViewUtilities
import SharedVars

def PrepareGui():
	GuiMainWindowBackgroundColor = 'magenta'
	SharedVars.GuiWindow.geometry(str(SharedVars.GuiMainWindowWidth) + 'x' + str(SharedVars.GuiMainWindowHeight) + '+' + str(SharedVars.GuiMainWindowLeft) + '+' + str(SharedVars.GuiMainWindowTop))
	SharedVars.GuiWindow.configure(background=GuiMainWindowBackgroundColor)
	SharedVars.GuiWindow.resizable(True, True)

	SharedVars.GuiDevelopmentMessageLabel.place(anchor='sw', relx=0.01,rely=0.99)
	SharedVars.GuiExitButton.place(anchor='se', relx=0.99, rely=0.99)

def GuiShowDevelopmentMessage(Text):
	SharedVars.GuiDevelopmentMessageLabel.configure(text=Text)
	
def ExitGui():
	SharedVars.GuiWindow.destroy()
	