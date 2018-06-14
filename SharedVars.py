import time
import tkinter as tk
from tkinter import ttk
import avro.schema
import IbViewEnums
import IbViewClasses
import IbViewGui

# Preferences file items
DataFilePath = ''
OutputPath = ''
DataFileDirectoryList = []
ListOfAllDataFileDescriptors = []
ListOfUnderlyingJsonDataFileDescriptors = []
ListOfUnderlyingAvroDataFileDescriptors = []
ListOfOptionJsonDataFileDescriptors = []
ListOfOptionAvroDataFileDescriptors = []
ListOfUnderlyingDataDayDescriptors = []
TotalNumberOfDataFilesInDirectory = 0
NumberOfUnderlyingJsonFiles = 0
NumberOfUnderlyingAvroFiles = 0
NumberOfOptionJsonFiles = 0
NumberOfOptionAvroFiles = 0
NumberOfOtherFiles = 0
UnderlyingEarliestDate = IbViewClasses.DateClass()
UnderlyingLatestDate = IbViewClasses.DateClass()

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

