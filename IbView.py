#!/home/bill/anaconda3/bin/python
import sys
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

	FooDate = IbViewClasses.DateClass()
	FooDate['year'] = SharedVars.ListOfUnderlyingDataFileDescriptors[10]['LogYear']
	FooDate['month'] = SharedVars.ListOfUnderlyingDataFileDescriptors[10]['LogMonth']
	FooDate['day'] = SharedVars.ListOfUnderlyingDataFileDescriptors[10]['LogDay']
	IbViewStorage.SiftUnderlyingDate(FooDate)

	IbViewGui.PrepareGui()
	SharedVars.GuiWindow.mainloop()

if __name__ == '__main__':
	Main()
	