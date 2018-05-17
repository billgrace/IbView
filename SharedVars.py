import tkinter as tk
from tkinter import ttk
import avro.schema
import IbViewEnums
import IbViewClasses
import IbViewGui

# Preferences file items
InputDirectoryPath = ''
OutputDirectoryPath = ''

# Gui - General
GuiMainWindowWidth = 1100
GuiMainWindowHeight = 700
GuiMainWindowLeft = 10
GuiMainWindowTop = 10
GuiRefreshInterval = 300
GuiWindow = tk.Tk()

# Gui - Miscellaneous
GuiDevelopmentMessageLabel = tk.Label(GuiWindow, text='(---)', fg='#055', bg='#8ff')
GuiExitButton = tk.Button(GuiWindow, text='Exit', command=IbViewGui.ExitGui)

