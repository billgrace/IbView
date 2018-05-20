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
	IbViewGui.PrepareGui()

	fromyear = str(SharedVars.UnderlyingEarliestDate['year'])
	toyear = str(SharedVars.UnderlyingLatestDate['year'])
	frommonth = str(SharedVars.UnderlyingEarliestDate['month'])
	tomonth = str(SharedVars.UnderlyingLatestDate['month'])
	fromday = str(SharedVars.UnderlyingEarliestDate['day'])
	today = str(SharedVars.UnderlyingLatestDate['day'])
	IbViewGui.GuiShowDevelopmentMessage(f'{SharedVars.TotalNumberOfDataFilesInDirectory} files, {SharedVars.NumberOfUnderlyingFiles} underlying files, from {frommonth}/{fromday}/{fromyear}/ to {tomonth}/{today}/{toyear}')

	SharedVars.GuiWindow.mainloop()

if __name__ == '__main__':
	Main()
	