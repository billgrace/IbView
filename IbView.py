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
	IbViewGui.PrepareGui()
	IbViewGui.RefreshGui()
	SharedVars.GuiWindow.mainloop()

if __name__ == '__main__':
	Main()
	