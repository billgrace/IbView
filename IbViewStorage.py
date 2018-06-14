import sys
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
		if FileName[11:25] == 'JsonUnderlying':
			SharedVars.NumberOfUnderlyingJsonFiles += 1
			FileDescriptor['FileType'] = 'UnderlyingJson'
			SharedVars.ListOfUnderlyingJsonDataFileDescriptors.append(FileDescriptor)
		elif FileName[11:21] == 'Underlying':
			SharedVars.NumberOfUnderlyingAvroFiles += 1
			FileDescriptor['FileType'] = 'UnderlyingAvro'
			SharedVars.ListOfUnderlyingAvroDataFileDescriptors.append(FileDescriptor)
		elif FileName[0:8] == 'SPX-Json':
			SharedVars.NumberOfOptionJsonFiles += 1
			FileDescriptor['FileType'] = 'OptionJson'
			FileDescriptor['StrikePrice'] = int(FileName[20:24])
			FileDescriptor['ExpirationYear'] = int(FileName[9:13])
			FileDescriptor['ExpirationMonth'] = int(FileName[14:16])
			FileDescriptor['ExpirationDay'] = int(FileName[17:19])
			if FileName[25] == 'P':
				FileDescriptor['ContractRight'] = 'PUT'
			else:
				FileDescriptor['ContractRight'] = 'CALL'
			FileDescriptor['QueuedHour'] = int(FileName[-25:-23])
			FileDescriptor['QueuedMinute'] = int(FileName[-22:-20])
			FileDescriptor['QueuedSecond'] = int(FileName[-19:-17])
			SharedVars.ListOfOptionJsonDataFileDescriptors.append(FileDescriptor)
		elif FileName[0:3] == 'SPX':
			SharedVars.NumberOfOptionAvroFiles += 1
			FileDescriptor['FileType'] = 'OptionAvro'
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
			SharedVars.ListOfOptionAvroDataFileDescriptors.append(FileDescriptor)
		else:
			SharedVars.NumberOfOtherFiles += 1
			FileDescriptor['FileType'] = 'Other'
			continue
		FileDescriptor['LogYear'] = int(FileName[-17:-13])
		FileDescriptor['LogMonth'] = int(FileName[-13:-11])
		FileDescriptor['LogDay'] = int(FileName[-11:-9])
		FileDescriptor['LogHour'] = float(FileName[-8:-4])

def GetUnderlyingDataDates():
	TestDate = IbViewClasses.DateClass()
	SharedVars.UnderlyingEarliestDate['year'] = 9999
	SharedVars.UnderlyingLatestDate['year'] = 0
	for FileDescriptor in SharedVars.ListOfUnderlyingAvroDataFileDescriptors:
		TestDate['year'] = FileDescriptor['LogYear']
		TestDate['month'] = FileDescriptor['LogMonth']
		TestDate['day'] = FileDescriptor['LogDay']
		if IbViewEnums.DateComparisonResult['FirstIsBeforeSecond'] == IbViewUtilities.CompareDates(TestDate, SharedVars.UnderlyingEarliestDate):
			SharedVars.UnderlyingEarliestDate['month'] = TestDate['month']
			SharedVars.UnderlyingEarliestDate['day'] = TestDate['day']
			SharedVars.UnderlyingEarliestDate['year'] = TestDate['year']
		if IbViewEnums.DateComparisonResult['FirstIsAfterSecond'] == IbViewUtilities.CompareDates(TestDate, SharedVars.UnderlyingLatestDate):
			SharedVars.UnderlyingLatestDate['month'] = TestDate['month']
			SharedVars.UnderlyingLatestDate['day'] = TestDate['day']
			SharedVars.UnderlyingLatestDate['year'] = TestDate['year']

def GetUnderlyingAvroFilenamesForDate(date):
	UnderlyingAvroFilesForThisDate = []
	print(date)
	print(f'Length of underlying file descriptor list: {len(SharedVars.ListOfUnderlyingAvroDataFileDescriptors)}')
	for FileDescriptor in SharedVars.ListOfUnderlyingAvroDataFileDescriptors:
		if FileDescriptor['LogYear'] == date['year'] and \
				FileDescriptor['LogMonth'] == date['month'] and \
				FileDescriptor['LogDay'] == date['day']:
			UnderlyingAvroFilesForThisDate.append(FileDescriptor['FileName'])
	returnList = sorted(UnderlyingAvroFilesForThisDate)
	return returnList

def SiftUnderlyingAvroDate(date):
	OutputFileName = 'SPXprice-' + str(date['year']) + '-' + str(date['month']) + '-' + str(date['day'])
	OutputFile = open(SharedVars.OutputPath + '/' + OutputFileName, 'wt')
	FilesToSift = GetUnderlyingAvroFilenamesForDate(date)
	InputFileName = FilesToSift[0]
	CurrentInputFile = open(SharedVars.DataFilePath + '/' + InputFileName, 'rt')
	OutputCaptureFile = open('/home/bill/SiftedData/PythonCapture.txt', 'wt')
	LineNumber = 0
	for Line in CurrentInputFile:
		LineNumber += 1
		TimeStampString, AvroStringWithByteTags = Line.split('---')
		AvroString = AvroStringWithByteTags[2:-2]
		AvroByteArray = IbViewUtilities.DecodeStringToBytes(AvroString)
		AvroByteStream = io.BytesIO(AvroByteArray)
		# if False:
		# 	print('!!!###*** Line: ' + str(LineNumber), file=OutputCaptureFile)
		# 	print(TimeStampString, file=OutputCaptureFile)
		# 	print(AvroString, file=OutputCaptureFile)
		# 	print(AvroByteArray, file=OutputCaptureFile)
		# else:
		try:
			reader = avro.datafile.DataFileReader(AvroByteStream, avro.io.DatumReader())
			for datum in reader:
				print('Line: ' + str(LineNumber) + ' at time ' + TimeStampString + ' has price at: ' + str(datum['Last']['Price']), file=OutputCaptureFile)
			reader.close()
		except Exception as e:
			print(f'Exception, line # {str(LineNumber)}: {str(e)}')
		AvroByteStream.close()
	OutputCaptureFile.close()
	CurrentInputFile.close()
	OutputFile.close()


	# for InputFileName in FilesToSift:
	# 	CurrentInputFile = open(SharedVars.DataFilePath + '/' + InputFileName, 'rt')
	# 	for Line in CurrentInputFile:
	# 		TimeStampString, AvroStringWithByteTags = Line.split('---')
	# 		AvroString = AvroStringWithByteTags[2:-2]
	# 		AvroByteArray = IbViewUtilities.DecodeStringToBytes(AvroString)
	# 		AvroByteStream = io.BytesIO(AvroByteArray)
	# 		reader = avro.datafile.DataFileReader(AvroByteStream, avro.io.DatumReader())
	# 		for datum in reader:
	# 			priceString = IbViewUtilities.StringFormatDollars(datum['Last']['Price'])
	# 		reader.close()
	# 		AvroByteStream.close()
	# 		OutputFile.write(TimeStampString + ', ' + priceString + '\n')
	# 	CurrentInputFile.close()
	# OutputFile.close()
