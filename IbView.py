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
	IbViewGui.PrepareGui()
	SharedVars.GuiWindow.mainloop()

if __name__ == '__main__':
	Main()
	