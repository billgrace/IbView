import time
import datetime
from tkinter import *
from tkinter import ttk

import IbView
import IbViewEnums
import IbViewClasses
import IbViewStorage
import IbViewUtilities
import SharedVars

def PrepareGui():
	GuiMainWindowBackgroundColor = 'magenta'
	SharedVars.GuiOSWindow.configure(background=GuiMainWindowBackgroundColor)
	SharedVars.GuiOSWindow.resizable(True, True)
	SharedVars.GuiOSWindow.bind_all('<KeyPress-F4>', ExitKeyPressed)
	SharedVars.GuiOSWindow.title('IbView')

	# Labels
	SharedVars.GuiFirstValidDateLabel.grid(column=0, row=0)
	SharedVars.GuiFirstValidDateLabel.configure(text = f'First valid data date: {IbViewUtilities.FormatDateShortMonth(SharedVars.FirstValidDataDate)}')
	SharedVars.GuiLastLoggedDateLabel.grid(column=0, row=1)
	SharedVars.GuiLastSiftedDateLabel.grid(column=0, row=2)
	SharedVars.GuiLastFilteredDateLabel.grid(column=0, row=3)
	SharedVars.GuiLastScaledDateLabel.grid(column=0, row=4)
	SharedVars.GuiLastShapedDateLabel.grid(column=0, row=5)
	SharedVars.GuiDevelopmentMessageLabel.grid(column=0, row=6)

	# Buttons
	SharedVars.GuiSiftButton.grid(column=1, row=2)
	SharedVars.GuiFilterButton.grid(column=1, row=3)
	SharedVars.GuiScaleButton.grid(column=1, row=4)
	SharedVars.GuiShapeButton.grid(column=1, row=5)
	SharedVars.GuiExitButton.grid(column=3, row=6)


	SharedVars.GuiRefreshWheelLabel.grid(column=2, row=6)
	SharedVars.GuiDevelopmentMessageLabel.grid(column=0, row=6)
	SharedVars.GuiExitButton.grid(column=3, row=6)

	SharedVars.GuiTextWindow.grid(column=2, row=0, columnspan=2, rowspan=6)
	SharedVars.GuiTextWindowVerticalScrollBar.place
	SharedVars.GuiTextWindow.insert(END, 'Hello, world.')
	SharedVars.GuiTextWindow.insert(END, '\nI say! Hello, world.')

def RefreshGui():
	SharedVars.GuiRefreshWheelIndex += 1
	if SharedVars.GuiRefreshWheelIndex >= len(SharedVars.GuiRefreshWheelChars):
		SharedVars.GuiRefreshWheelIndex = 0
	SharedVars.GuiRefreshWheelLabel.configure(text = SharedVars.GuiRefreshWheelChars[SharedVars.GuiRefreshWheelIndex])
	SharedVars.GuiOSWindow.after(SharedVars.GuiRefreshInterval, RefreshGui)

def Sift():
	IbViewUtilities.EmptyTextWindow()
	RightNow = datetime.datetime.today()
	if RightNow.hour > 19:
		SharedVars.LastValidDataDate = datetime.date(RightNow.year, RightNow.month, RightNow.day)
	else:
		SharedVars.LastValidDataDate = datetime.date(RightNow.year, RightNow.month, RightNow.day) - datetime.timedelta(days=1)
	SiftDate = SharedVars.FirstValidDataDate
	while SiftDate <= SharedVars.LastValidDataDate:
		if IbViewUtilities.DateIsATradingDay(SiftDate):
			if IbViewUtilities.DateIsAlreadySifted(SiftDate):
				IbViewUtilities.AddLineToTextWindow(f'{IbViewUtilities.FormatDateShortMonth(SiftDate)} has already been sifted')
			else:
				IbViewUtilities.AddLineToTextWindow(f'Sifting {IbViewUtilities.FormatDateShortMonth(SiftDate)}')
				IbViewStorage.SiftUnderlyingAvroDate(SiftDate)
				SharedVars.LastSiftedDate = SiftDate
		else:
			IbViewUtilities.AddLineToTextWindow(f'{IbViewUtilities.FormatDateShortMonth(SiftDate)} is not a trading day')
		SharedVars.GuiWindow.update()
		SiftDate += datetime.timedelta(days=1)
	SharedVars.GuiLastSiftedDateLabel.configure(text = f'Last sifted date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastSiftedDate)}')

def Filter():
	SharedVars.GuiLastFilteredDateLabel.configure(text = f'Last filtered date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastFilteredDate)}')

def Scale():
	SharedVars.GuiLastScaledDateLabel.configure(text = f'Last scaled date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastScaledDate)}')

def Shape():
	SharedVars.GuiLastShapedDateLabel.configure(text = f'Last shaped date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastShapedDate)}')

def GuiShowDevelopmentMessage(Text):
	SharedVars.GuiDevelopmentMessageLabel.configure(text=Text)
	
def ExitKeyPressed(KeyPressEvent):
	ExitGui()

def ExitGui():
	SharedVars.GuiOSWindow.destroy()
	