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
	SharedVars.GuiLastCheckedDateLabel.grid(column=0, row=4)
	SharedVars.GuiLastScaledDateLabel.grid(column=0, row=5)
	SharedVars.GuiLastShapedDateLabel.grid(column=0, row=6)
	SharedVars.GuiDevelopmentMessageLabel.grid(column=0, row=7)

	# Buttons
	SharedVars.GuiSiftButton.grid(column=1, row=2)
	SharedVars.GuiFilterButton.grid(column=1, row=3)
	SharedVars.GuiCheckButton.grid(column=1, row=4)
	SharedVars.GuiScaleButton.grid(column=1, row=5)
	SharedVars.GuiShapeButton.grid(column=1, row=6)
	SharedVars.GuiExitButton.grid(column=3, row=7)


	SharedVars.GuiRefreshWheelLabel.grid(column=2, row=7)
	SharedVars.GuiDevelopmentMessageLabel.grid(column=0, row=7)
	SharedVars.GuiExitButton.grid(column=3, row=7)

	SharedVars.GuiTextWindow.grid(column=2, row=0, columnspan=2, rowspan=7)
	SharedVars.GuiTextWindowVerticalScrollBar.place
	SharedVars.GuiTextWindow.insert(END, 'Hello, world.')
	SharedVars.GuiTextWindow.insert(END, '\nI say! Hello, world.')

def RefreshGui():
	SharedVars.GuiRefreshWheelIndex += 1
	if SharedVars.GuiRefreshWheelIndex >= len(SharedVars.GuiRefreshWheelChars):
		SharedVars.GuiRefreshWheelIndex = 0
	SharedVars.GuiRefreshWheelLabel.configure(text = SharedVars.GuiRefreshWheelChars[SharedVars.GuiRefreshWheelIndex])
	SharedVars.GuiOSWindow.after(SharedVars.GuiRefreshInterval, RefreshGui)

def SetLastValidDataDate():
	RightNow = datetime.datetime.today()
	if RightNow.hour > 19:
		SharedVars.LastValidDataDate = datetime.date(RightNow.year, RightNow.month, RightNow.day)
	else:
		SharedVars.LastValidDataDate = datetime.date(RightNow.year, RightNow.month, RightNow.day) - datetime.timedelta(days=1)

def Sift():
	IbViewUtilities.EmptyTextWindow()
	SetLastValidDataDate()
	SiftDate = SharedVars.FirstValidDataDate
	SharedVars.TotalSiftedDaysAvailable = 0
	while SiftDate <= SharedVars.LastValidDataDate:
		if IbViewUtilities.DateIsATradingDay(SiftDate):
			SharedVars.TotalSiftedDaysAvailable += 1
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
	SharedVars.GuiLastSiftedDateLabel.configure(text = f'Last sifted date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastSiftedDate)}\nDays available: {SharedVars.TotalSiftedDaysAvailable}')
	IbViewUtilities.AddLineToTextWindow('Sifting is finished')
	SharedVars.GuiWindow.update()

def Filter():
	IbViewUtilities.EmptyTextWindow()
	SetLastValidDataDate()
	FilterDate = SharedVars.FirstValidDataDate
	while FilterDate <= SharedVars.LastValidDataDate:
		if IbViewUtilities.DateIsATradingDay(FilterDate):
			if IbViewUtilities.DateIsAlreadyFiltered(FilterDate):
				IbViewUtilities.AddLineToTextWindow(f'{IbViewUtilities.FormatDateShortMonth(FilterDate)} has already been filtered')
			else:
				IbViewUtilities.AddLineToTextWindow(f'Filtering {IbViewUtilities.FormatDateShortMonth(FilterDate)}')
				IbViewStorage.FilterUnderlyingDate(FilterDate)
				SharedVars.LastFilteredDate = FilterDate
		else:
			IbViewUtilities.AddLineToTextWindow(f'{IbViewUtilities.FormatDateShortMonth(FilterDate)} is not a trading day')
		SharedVars.GuiWindow.update()
		FilterDate += datetime.timedelta(days=1)
	SharedVars.GuiLastFilteredDateLabel.configure(text = f'Last filtered date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastFilteredDate)}')
	IbViewUtilities.AddLineToTextWindow('Filtering is finished')
	SharedVars.GuiWindow.update()

def Check():
	IbViewUtilities.EmptyTextWindow()
	SetLastValidDataDate()
	CheckDate = SharedVars.FirstValidDataDate
	while CheckDate <= SharedVars.LastValidDataDate:
		if IbViewUtilities.DateIsATradingDay(CheckDate):
			if IbViewUtilities.DateIsAlreadyChecked(CheckDate):
				IbViewUtilities.AddTextToTextWindow(f'{IbViewUtilities.FormatDateShortMonth(CheckDate)}')
			else:
				IbViewUtilities.AddTextToTextWindow(f'Checking {IbViewUtilities.FormatDateShortMonth(CheckDate)}')
				IbViewStorage.CheckUnderlyingDate(CheckDate)
				SharedVars.LastCheckedDate = CheckDate
		else:
			IbViewUtilities.AddTextToTextWindow(f'{IbViewUtilities.FormatDateShortMonth(CheckDate)} is not a trading day')
		SharedVars.GuiWindow.update()
		CheckDate += datetime.timedelta(days=1)
	SharedVars.GuiLastCheckedDateLabel.configure(text = f'Last Checked date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastCheckedDate)}')
	IbViewUtilities.AddLineToTextWindow('\n\nChecking is finished')
	SharedVars.GuiWindow.update()

def ScaleAllIntervals():
	IbViewStorage.ScaleUnderlying('Second', 20)
	IbViewStorage.ScaleUnderlying('Second', 30)
	IbViewStorage.ScaleUnderlying('Second', 40)
	IbViewStorage.ScaleUnderlying('Minute', 1)
	IbViewStorage.ScaleUnderlying('Minute', 5)
	IbViewStorage.ScaleUnderlying('Minute', 10)
	IbViewStorage.ScaleUnderlying('Minute', 15)
	IbViewStorage.ScaleUnderlying('Minute', 30)
	IbViewStorage.ScaleUnderlying('Hour', 1)
	IbViewStorage.ScaleUnderlying('Hour', 2)

def Scale():
	IbViewUtilities.EmptyTextWindow()
	ScaleAllIntervals()
	SharedVars.GuiLastScaledDateLabel.configure(text = f'Last scaled date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastScaledDate)}')
	IbViewUtilities.AddLineToTextWindow('Scaling is finished')
	SharedVars.GuiWindow.update()

def Shape():
	IbViewUtilities.EmptyTextWindow()
	SharedVars.GuiWindow.update()
	IbViewStorage.ShapeAllScaledData()
	SharedVars.GuiLastShapedDateLabel.configure(text = f'Last shaped date: {IbViewUtilities.FormatDateShortMonth(SharedVars.LastShapedDate)}')
	IbViewUtilities.AddLineToTextWindow('Shaping is finished')
	SharedVars.GuiWindow.update()

def GuiShowDevelopmentMessage(Text):
	SharedVars.GuiDevelopmentMessageLabel.configure(text=Text)
	
def ExitKeyPressed(KeyPressEvent):
	ExitGui()

def ExitGui():
	SharedVars.GuiOSWindow.destroy()
	