import time
import datetime
from tkinter import *
from tkinter import ttk
import avro.schema
import IbViewEnums
import IbViewClasses
import IbViewGui

# Raw logged data
FirstValidDataDate = datetime.date(2018, 6, 18)
LastValidDataDate = datetime.date(2000, 1, 1)
UnderlyingEarliestDate = datetime.date(2000, 1, 1)
UnderlyingLatestDate = datetime.date(2000, 1, 1)
LoggedDataFilePath = ''
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
NumberOfDaysInASample = 20

# Sift, Filter, Scale, Shape
SiftedDataPath = ''
FilteredDataPath = ''
CheckedDataPath = ''
ScaledDataPath = ''
ShapedDataPath = ''
LastSiftedDate = datetime.date(2000, 1, 1)
LastFilteredDate = datetime.date(2000, 1, 1)
LastCheckedDate = datetime.date(2000, 1, 1)
LastScaledDate = datetime.date(2000, 1, 1)
LastShapedDate = datetime.date(2000, 1, 1)
TotalSiftedDaysAvailable = 0

# Gui - General
GuiOSWindow = Tk()
GuiWindow = ttk.Frame(GuiOSWindow, padding="3 3 12 12")
GuiWindow.grid(column=0, row=0, sticky=(N+W+E+S))

# Gui - Refresh
GuiRefreshInterval = 300
GuiRefreshWheelChars = ['|', '/', '-', '\\', 'O', '0', 'o', '_', '.']
GuiRefreshWheelIndex = 0
GuiRefreshWheelLabel = Label(GuiWindow)

# Gui - Labels
GuiFirstValidDateLabel = Label(GuiWindow)
GuiLastLoggedDateLabel = Label(GuiWindow)
GuiLastSiftedDateLabel = Label(GuiWindow, text = 'Last sifted date: (---)')
GuiLastFilteredDateLabel = Label(GuiWindow, text = 'Last filtered date: (---)')
GuiLastCheckedDateLabel = Label(GuiWindow, text = 'Last checked date: (---)')
GuiLastScaledDateLabel = Label(GuiWindow, text = 'Last scaled date: (---)')
GuiLastShapedDateLabel = Label(GuiWindow, text = 'Last shaped date: (---)')
GuiDevelopmentMessageLabel = Label(GuiWindow, text='(---)', fg='#055', bg='#8ff')

# Gui - Buttons
GuiSiftButton = Button(GuiWindow, text='Sift', command=IbViewGui.Sift)
GuiFilterButton = Button(GuiWindow, text='Filter', command=IbViewGui.Filter)
GuiCheckButton = Button(GuiWindow, text='Check', command=IbViewGui.Check)
GuiScaleButton = Button(GuiWindow, text='Scale', command=IbViewGui.Scale)
GuiShapeButton = Button(GuiWindow, text='Shape', command=IbViewGui.Shape)
GuiExitButton = Button(GuiWindow, text='Exit', command=IbViewGui.ExitGui)

# Gui - Text window
GuiTextWindowWidth = 80	# width in characters
GuiTextWindowHeight = 40 # height in lines
GuiTextWindowRight = 0.95
GuiTextWindowTop = 0.1

GuiTextWindow = Text(GuiWindow, width=GuiTextWindowWidth, height=GuiTextWindowHeight, wrap='word')
GuiTextWindowVerticalScrollBar = Scrollbar(GuiWindow, orient=VERTICAL, command=GuiTextWindow.yview)
GuiTextWindowHorizontalScrollBar = Scrollbar(GuiWindow, orient=HORIZONTAL, command=GuiTextWindow.xview)
GuiTextWindow.configure(yscrollcommand=GuiTextWindowVerticalScrollBar.set)
GuiTextWindow.configure(xscrollcommand=GuiTextWindowHorizontalScrollBar.set)

