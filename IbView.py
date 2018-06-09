#!/home/bill/anaconda3/bin/python
import sys
import SharedVars
import IbViewEnums
import IbViewClasses
import IbViewStorage
import IbViewGui
import IbViewUtilities

#a fake change to this file.

def Main():
	IbViewStorage.ReadPreferencesFile()
	IbViewStorage.GetDataFileDescriptors()
	IbViewStorage.GetUnderlyingDataDates()

	FooDate = IbViewClasses.DateClass()
	# FooDate['year'] = SharedVars.ListOfUnderlyingDataFileDescriptors[10]['LogYear']
	# FooDate['month'] = SharedVars.ListOfUnderlyingDataFileDescriptors[10]['LogMonth']
	# FooDate['day'] = SharedVars.ListOfUnderlyingDataFileDescriptors[10]['LogDay']
	FooDate['year'] = 2018
	FooDate['month'] = 5
	FooDate['day'] = 9
	IbViewStorage.SiftUnderlyingDate(FooDate)

	IbViewGui.PrepareGui()
	SharedVars.GuiWindow.mainloop()

if __name__ == '__main__':
	Main()
	