#!/home/bill/anaconda3/bin/python
import sys
import os
import datetime
import SharedVars
import IbViewEnums
import IbViewClasses
import IbViewStorage
import IbViewGui
import IbViewUtilities

def Main():
	IbViewStorage.ReadPreferencesFile()
	IbViewStorage.GetDataFileDescriptors()
	IbViewStorage.GetUnderlyingDataDates()

	FirstValidDataDate = datetime.date(2018, 6, 18)
	RightNow = datetime.datetime.today()
	if RightNow.hour > 19:
		LastValidDataDate = datetime.date(RightNow.year, RightNow.month, RightNow.day)
	else:
		LastValidDataDate = datetime.date(RightNow.year, RightNow.month, RightNow.day) - datetime.timedelta(days=1)
	SiftDate = FirstValidDataDate
	SiftDateStructure = IbViewClasses.DateClass()
	while SiftDate <= LastValidDataDate:
		SiftDateStructure['year'] = SiftDate.year
		SiftDateStructure['month'] = SiftDate.month
		SiftDateStructure['day'] = SiftDate.day
		if IbViewUtilities.DateIsATradingDay(SiftDateStructure):
			if IbViewUtilities.DateIsAlreadySifted(SiftDateStructure):
				print(f'{SiftDateStructure} has already been sifted')
			else:
				print(f'Sifting {SiftDateStructure}')
				IbViewStorage.SiftUnderlyingAvroDate(SiftDateStructure)
		else:
			print(f'{SiftDateStructure} is not a trading day')
		SiftDate += datetime.timedelta(days=1)

	IbViewGui.PrepareGui()
	SharedVars.GuiWindow.mainloop()

if __name__ == '__main__':
	Main()
	