import sys
import os
import io
import datetime
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
				elif(KeyWord == 'SiftedDataPath'):
					SharedVars.SiftedDataPath = KeyValue
				elif(KeyWord == 'FilteredDataPath'):
					SharedVars.FilteredDataPath = KeyValue
				elif(KeyWord == 'ScaledDataPath'):
					SharedVars.ScaledDataPath = KeyValue
				elif(KeyWord == 'ShapedDataPath'):
					SharedVars.ShapedDataPath = KeyValue
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
	TestDate = datetime.date(2000, 1, 1)
	SharedVars.UnderlyingEarliestDate.replace(year = 9999)
	SharedVars.UnderlyingLatestDate.replace(year = 1)
	for FileDescriptor in SharedVars.ListOfUnderlyingAvroDataFileDescriptors:
		TestDate.replace(year = FileDescriptor['LogYear'])
		TestDate.replace(month = FileDescriptor['LogMonth'])
		TestDate.replace(day = FileDescriptor['LogDay'])
		if IbViewEnums.DateComparisonResult['FirstIsBeforeSecond'] == IbViewUtilities.CompareDates(TestDate, SharedVars.UnderlyingEarliestDate):
			SharedVars.UnderlyingEarliestDate.replace(month = TestDate.month)
			SharedVars.UnderlyingEarliestDate.replace(day = TestDate.day)
			SharedVars.UnderlyingEarliestDate.replace(year = TestDate.year)
		if IbViewEnums.DateComparisonResult['FirstIsAfterSecond'] == IbViewUtilities.CompareDates(TestDate, SharedVars.UnderlyingLatestDate):
			SharedVars.UnderlyingLatestDate.replace(month = TestDate.month)
			SharedVars.UnderlyingLatestDate.replace(day = TestDate.day)
			SharedVars.UnderlyingLatestDate.replace(year = TestDate.year)

def GetUnderlyingJsonFilenamesForDate(date):
	UnderlyingJsonFilesForThisDate = []
	for FileDescriptor in SharedVars.ListOfUnderlyingJsonDataFileDescriptors:
		if FileDescriptor['LogYear'] == date.year and \
				FileDescriptor['LogMonth'] == date.month and \
				FileDescriptor['LogDay'] == date.day:
			UnderlyingJsonFilesForThisDate.append(FileDescriptor['FileName'])
	returnList = sorted(UnderlyingJsonFilesForThisDate)
	return returnList

def GetUnderlyingAvroFilenamesForDate(date):
	UnderlyingAvroFilesForThisDate = []
	for FileDescriptor in SharedVars.ListOfUnderlyingAvroDataFileDescriptors:
		if FileDescriptor['LogYear'] == date.year and \
				FileDescriptor['LogMonth'] == date.month and \
				FileDescriptor['LogDay'] == date.day:
			UnderlyingAvroFilesForThisDate.append(FileDescriptor['FileName'])
	returnList = sorted(UnderlyingAvroFilesForThisDate)
	return returnList

def SiftUnderlyingAvroDate(date):
	# Input is raw, logged data files. Each file covers one hour of a trading day. Contents are text lines with time code and avro-serialized market data.
	# Output is one file per trading day. Each line of text is time stamp and SPX value. There's one line per 10 seconds through the trading day.
	# OutputFileName = 'SPXprice-' + str(date.year) + '-' + str(date.month) + '-' + str(date.day) + '.csv'
	OutputFileName = f'SPXprice-{date.year:4}-{date.month:02}-{date.day:02}.csv'
	OutputFile = open(SharedVars.SiftedDataPath + '/' + OutputFileName, 'wt')
	JsonFilesToSift = GetUnderlyingJsonFilenamesForDate(date)
	AvroFilesToSift = GetUnderlyingAvroFilenamesForDate(date)
	FileNameIndex = 0
	# for InputFileName in AvroFilesToSift:
	for InputFileNameIndex in range(0, len(AvroFilesToSift)):
		JsonInputFileName = JsonFilesToSift[InputFileNameIndex]
		AvroInputFileName = AvroFilesToSift[InputFileNameIndex]
		CurrentJsonInputFile = open(SharedVars.DataFilePath + '/' + JsonInputFileName, 'rt')
		CurrentAvroInputFile = open(SharedVars.DataFilePath + '/' + AvroInputFileName, 'rt')
		# OutputCaptureFile = open('/home/bill/SiftedData/PythonCapture.txt', 'wt')
		FileLineNumber = 0
		for AvroFileLine in CurrentAvroInputFile:
			JsonFileLine = CurrentJsonInputFile.readline()
			FileLineNumber += 1
			TimeStampString, AvroStringWithByteTags = AvroFileLine.split('---')
			HourString = TimeStampString[22:24]
			MinuteString = TimeStampString[25:27]
			SecondString = TimeStampString[28:30]
			MillisecondString = TimeStampString[31:34]
			AvroString = AvroStringWithByteTags[2:-2]
			AvroByteArray = IbViewUtilities.DecodeStringToBytes(AvroString)
			AvroByteStream = io.BytesIO(AvroByteArray)
			try:
				reader = avro.datafile.DataFileReader(AvroByteStream, avro.io.DatumReader())
				for datum in reader:
					# print('Line: ' + str(LineNumber) + ' at time ' + TimeStampString + ' has price at: ' + str(datum['Last']['Price']), file=OutputCaptureFile)
					# print('Line: ' + str(FileLineNumber) + ' at time ' + TimeStampString + ' has price at: ' + str(datum['Last']['Price']), file=OutputFile)
					print(HourString + ', ' + MinuteString + ', ' + SecondString + ', ' + MillisecondString + ', ' + str(datum['Last']['Price']), file=OutputFile)
				reader.close()
			except Exception as e:
				ex_type, ex_value, ex_traceback = sys.exc_info()
				print(f'\n!!! Exception, file {AvroInputFileName}, line # {str(FileLineNumber)}: {str(e)}, {ex_type.__name__} {ex_value}', file=OutputFile)
				print(AvroString, file=OutputFile)
				print(AvroByteArray, file=OutputFile)
				print(JsonFileLine, file=OutputFile)
			AvroByteStream.close()
		CurrentJsonInputFile.close()
		CurrentAvroInputFile.close()
	OutputFile.close()

def FilterUnderlyingDate(date):
	# Input is the output from the Sifting stage.
	# Output is the same as the input with lines trimmed omitted for entries before 6:30 AM, after 1:00 PM, or having SPX value < 1,000 or > 10,000
	FileName = f'SPXprice-{date.year:4}-{date.month:02}-{date.day:02}.csv'
	InputFile = open(SharedVars.SiftedDataPath + '/' + FileName, 'rt')
	OutputFile = open(SharedVars.FilteredDataPath + '/' + FileName, 'wt')
	for CurrentLine in InputFile:
		KeepThisLine = True
		FilteringIsComplete = False
		ThisLineValues = CurrentLine.split(',')
		ThisHour = int(ThisLineValues[0])
		ThisMinute = int(ThisLineValues[1])
		ThisSecond = int(ThisLineValues[2])
		ThisMillisecond = int(ThisLineValues[3])
		ThisValue = float(ThisLineValues[4])
		# Drop times before 6:30 AM
		if ThisHour < 6:
			KeepThisLine = False
		if ThisHour == 6 and ThisMinute < 30:
			KeepThisLine = False
		# Keep the first line with hour == 1:00 PM and break to skip all later lines
		if ThisHour == 13:
			FilteringIsComplete = True
		# Drop values < 1,000.0
		if ThisValue < 1000.0:
			KeepThisLine = False
		# Drop values > 10,000.0
		if ThisValue > 10000.0:
			KeepThisLine = False
		if KeepThisLine:
			print(CurrentLine, end='', file=OutputFile)
		if FilteringIsComplete:
			break
	InputFile.close()
	OutputFile.close()

def ScaleUnderlying(IntervalName, IntervalQuantity, AverageFlag):
	# Are we averaging or sampling?
	if AverageFlag:
		AverageLetter = 'A'
	else:
		AverageLetter = 'S'
	# Set up the single output file we're making and traverse all the input files
	OutputFileName = f'SPX{str(IntervalQuantity)}{IntervalName}{AverageLetter}.csv'
	OutputFile = open(SharedVars.ScaledDataPath + '/' + OutputFileName, 'wt')
	InputFileNameList = sorted(os.listdir(SharedVars.FilteredDataPath))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
	for InputFileName in InputFileNameList:
		InputFile = open(SharedVars.FilteredDataPath + '/' + InputFileName, 'rt')
		# For each input file, set up the date strings for the output file lines
		InputFileNameParts = InputFileName.split('-')
		YearString = InputFileNameParts[1]
		MonthString = InputFileNameParts[2]
		DayString = InputFileNameParts[3][0:2]
		# Figure out the requested scaling in terms of how many one-per-10-second input
		#  lines we'll boil down to each line in the output file
		ScaleCount = 10	# fake value in case we have to error out on a bad interval definition
		if IntervalName == 'Second':
			if IntervalQuantity == 20:
				ScaleCount = 2
			elif IntervalQuantity == 30:
				ScaleCount = 3
			elif IntervalQuantity == 40:
				ScaleCount = 4
			else:
				IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Seconds')
		elif IntervalName == 'Minute':
			if IntervalQuantity == 1:
				ScaleCount = 6
			elif IntervalQuantity == 5:
				ScaleCount = 30
			elif IntervalQuantity == 10:
				ScaleCount = 60
			elif IntervalQuantity == 15:
				ScaleCount = 90
			elif IntervalQuantity ==30:
				ScaleCount = 180
			else:
				IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Minutes')
		elif IntervalName == 'Hour':
			if IntervalQuantity == 1:
				ScaleCount = 360
			elif IntervalQuantity == 2:
				ScaleCount = 720
			else:
				IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Hours')
		# We want to sample the SPX value and time stamp at approximately the middle of the
		#  batch of input lines being processed into each output line
		ScaleHalfCount = int(ScaleCount/2)
		ScaleCounter = 0
		ValueAccumulator = 0.0
		for InputFileLine in InputFile:
			InputFileLineParts = InputFileLine.split(',')
			ValueAccumulator += float(InputFileLineParts[4])
			ScaleCounter += 1
			if ScaleCounter == ScaleHalfCount:
				HourString = InputFileLineParts[0]
				MinuteString = InputFileLineParts[1]
				SecondString = InputFileLineParts[2]
				SampledValueString = InputFileLineParts[4]
			if ScaleCounter == ScaleCount:
				AveragedValueString = f'{(ValueAccumulator/ScaleCount):.2f}'
				ScaleCounter = 0
				ValueAccumulator = 0.0
				if AverageFlag:
					print(f'{YearString}, {MonthString}, {DayString}, {HourString}, {MinuteString}, {SecondString}, {AveragedValueString}', file=OutputFile)
				else:
					print(f'{YearString}, {MonthString}, {DayString}, {HourString}, {MinuteString}, {SecondString}, {SampledValueString}', end='', file=OutputFile)
		InputFile.close()
	OutputFile.close()
