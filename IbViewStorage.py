import os
import io
import avro.datafile
import avro.io

import IbViewEnums
import IbViewClasses
import IbViewGui
import IbViewUtilities
import SharedVars

def ReadPreferencesFile():
	try:
		# yet another fake change to try to get git savvy sync'd up
		PreferenceFile = open('preferences.cfg', 'r')
		LineNumber = 0
		for Line in PreferenceFile:
			LineNumber += 1
			if Line[0] == '#':
				continue
			try:
				UnstrippedKeyWord, UnstrippedKeyValue = Line.split('=')
				KeyWord = UnstrippedKeyWord.strip()
				KeyValue = UnstrippedKeyValue.strip()
				if(KeyWord == 'DataFilePath'):
					SharedVars.DataFilePath = KeyValue
				elif(KeyWord == 'OutputPath'):
					SharedVars.OutputPath = KeyValue
				else:
					IbViewUtilities.LogError('unrecognized preference.cfg KeyWord: ' + KeyWord + ' on line #' + str(LineNumber))
			except Exception as e:
				IbViewUtilities.LogError('problem parsing preference.cfg line #' + str(LineNumber) + ': ' + Line + ', exception: ' + str(e))
	except Exception as e:
		IbViewUtilities.LogError('unable to open Preferences.cfg - ' + str(e))

def GetDataFileDescriptors():
	SharedVars.DataFileDirectoryList = os.listdir(SharedVars.DataFilePath)
	SharedVars.TotalNumberOfDataFilesInDirectory = len(SharedVars.DataFileDirectoryList)
	for CurrentIndex in range(0, len(SharedVars.DataFileDirectoryList)-1):
		FileDescriptor = IbViewClasses.DataFileDescriptor()
		FileName = SharedVars.DataFileDirectoryList[CurrentIndex]
		FileDescriptor['FileName'] = FileName
		if FileName[0:3] == 'SPX':
			SharedVars.NumberOfOptionFiles += 1
			FileDescriptor['FileType'] = 'Option'
			FileDescriptor['StrikePrice'] = int(FileName[15:19])
			FileDescriptor['ExpirationYear'] = int(FileName[4:8])
			FileDescriptor['ExpirationMonth'] = int(FileName[9:11])
			FileDescriptor['ExpirationDay'] = int(FileName[12:14])
			if FileName[20] == 'P':
				FileDescriptor['ContractRight'] = 'PUT'
			else:
				FileDescriptor['ContractRight'] = 'CALL'
			FileDescriptor['QueuedHour'] = int(FileName[-25:-23])
			FileDescriptor['QueuedMinute'] = int(FileName[-22:-20])
			FileDescriptor['QueuedSecond'] = int(FileName[-19:-17])
			FileDescriptor['LogYear'] = int(FileName[-17:-13])
			FileDescriptor['LogMonth'] = int(FileName[-13:-11])
			FileDescriptor['LogDay'] = int(FileName[-11:-9])
			FileDescriptor['LogHour'] = float(FileName[-8:-4])
			SharedVars.ListOfOptionDataFileDescriptors.append(FileDescriptor)
		elif FileName[11:21] == 'Underlying':
			SharedVars.NumberOfUnderlyingFiles += 1
			FileDescriptor['FileType'] = 'Underlying'
			FileDescriptor['LogYear'] = int(FileName[-17:-13])
			FileDescriptor['LogMonth'] = int(FileName[-13:-11])
			FileDescriptor['LogDay'] = int(FileName[-11:-9])
			FileDescriptor['LogHour'] = float(FileName[-8:-4])
			SharedVars.ListOfUnderlyingDataFileDescriptors.append(FileDescriptor)
		else:
			SharedVars.NumberOfOtherFiles += 1
			FileDescriptor['FileType'] = 'Other'
		# SharedVars.ListOfAllDataFileDescriptors.append(FileDescriptor)

def GetUnderlyingDataDates():
	TestDate = IbViewClasses.DateClass()
	SharedVars.UnderlyingEarliestDate['year'] = 9999
	SharedVars.UnderlyingLatestDate['year'] = 0
	for FileDescriptor in SharedVars.ListOfUnderlyingDataFileDescriptors:
		TestDate['year'] = FileDescriptor['LogYear']
		TestDate['month'] = FileDescriptor['LogMonth']
		TestDate['day'] = FileDescriptor['LogDay']
		if IbViewEnums.DateComparisonResult['FirstIsBeforeSecond'] == IbViewUtilities.CompareDates(TestDate, SharedVars.UnderlyingEarliestDate):
			SharedVars.UnderlyingEarliestDate = TestDate
		if IbViewEnums.DateComparisonResult['FirstIsAfterSecond'] == IbViewUtilities.CompareDates(TestDate, SharedVars.UnderlyingLatestDate):
			SharedVars.UnderlyingLatestDate = TestDate
