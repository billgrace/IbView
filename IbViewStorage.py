import sys
import os
import io
import datetime
import math
import avro.datafile
import avro.io
import pandas as pd
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
				if KeyWord == 'DataFilePath':
					SharedVars.DataFilePath = KeyValue
				elif KeyWord == 'SiftedDataPath':
					SharedVars.SiftedDataPath = KeyValue
				elif KeyWord == 'FilteredDataPath':
					SharedVars.FilteredDataPath = KeyValue
				elif KeyWord == 'CheckedDataPath':
					SharedVars.CheckedDataPath = KeyValue
				elif KeyWord == 'ScaledDataPath':
					SharedVars.ScaledDataPath = KeyValue
				elif KeyWord == 'ShapedDataPath':
					SharedVars.ShapedDataPath = KeyValue
				elif KeyWord == 'NumberOfDaysInASample':
					SharedVars.NumberOfDaysInASample = int(KeyValue)
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
		ThisLineParts = CurrentLine.split(',')
		ThisHour = int(ThisLineParts[0])
		ThisMinute = int(ThisLineParts[1])
		ThisSecond = int(ThisLineParts[2])
		ThisMillisecond = int(ThisLineParts[3])
		ThisValue = float(ThisLineParts[4])
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

def CheckUnderlyingDate(date):
	# Input is the daily filtered files
	# Output is those same files IF they pass a comparison to
	#  online open, high, low, close values
	# For starts, lets insist on comparisons being within 1%
	FileName = f'SPXprice-{date.year:4}-{date.month:02}-{date.day:02}.csv'
	InputFile = open(SharedVars.FilteredDataPath + '/' + FileName, 'rt')
	OurOpenValue = -1.0
	OurHighValue = -1.0
	OurLowValue = 1000000.
	OurCloseValue = 1.0
	for CurrentLine in InputFile:
		ThisLineParts = CurrentLine.split(',')
		ThisValue = float(ThisLineParts[4])
		# If OpenValue is negative, this must be the first entry which is our opening value
		if OurOpenValue < 0:
			OurOpenValue = ThisValue
		# ALWAYS update the closing value and it will end up being the last one in the file
		OurCloseValue = ThisValue
		if ThisValue > OurHighValue:
			OurHighValue = ThisValue
		if ThisValue < OurLowValue:
			OurLowValue = ThisValue
	InputFile.close()
	# OK, we now have OUR version of open, high, low, close for the date...
	# Let's get Yahoo's version
	DateString = date.strftime('%b %d, %Y')
	DataFramesInPage = pd.read_html('https://finance.yahoo.com/quote/%5EGSPC/history')
	SpxHistoryDataFrame = DataFramesInPage[0]
	DateRowIndex = SpxHistoryDataFrame['Date'] == DateString
	YahooOpenValue = SpxHistoryDataFrame.loc[DateRowIndex, 'Open'].iat[0]
	YahooHighValue = SpxHistoryDataFrame.loc[DateRowIndex, 'High'].iat[0]
	YahooLowValue = SpxHistoryDataFrame.loc[DateRowIndex, 'Low'].iat[0]
	YahooCloseValue = SpxHistoryDataFrame.loc[DateRowIndex, 'Close*'].iat[0]
	OpenDifference = abs(YahooOpenValue - OurOpenValue)/OurOpenValue * 100
	HighDifference = abs(YahooHighValue - OurHighValue)/OurHighValue * 100
	LowDifference = abs(YahooLowValue - OurLowValue)/OurLowValue * 100
	CloseDifference = abs(YahooCloseValue - OurCloseValue)/OurCloseValue * 100
	DifferenceIsAcceptable = True
	DifferenceString = ''
	if OpenDifference > 1.0:
		DifferenceString += f' Open diff: {OpenDifference:0.1f}'
		DifferenceIsAcceptable = False
	if HighDifference > 1.0:
		DifferenceString += f' High diff: {HighDifference:0.1f}'
		DifferenceIsAcceptable = False
	if LowDifference > 1.0:
		DifferenceString += f' Low diff: {LowDifference:0.1f}'
		DifferenceIsAcceptable = False
	if CloseDifference > 1.0:
		DifferenceString += f' Close diff: {CloseDifference:0.1f}'
		DifferenceIsAcceptable = False
	if not DifferenceIsAcceptable:
		# Announce excessive difference to GUI
		IbViewUtilities.AddLineToTextWindow('\n\n' + IbViewUtilities.FormatDateShortMonth(date) + ' - ' + DifferenceString + '\n')
	else:
		# Copy acceptable date file to 'Checked' directory
		InputFile = open(SharedVars.FilteredDataPath + '/' + FileName, 'rt')
		OutputFile = open(SharedVars.CheckedDataPath + '/' + FileName, 'wt')
		for CurrentLine in InputFile:
			print(CurrentLine, end='', file=OutputFile)
		OutputFile.close()
		InputFile.close()

def ScaleUnderlying(IntervalUnit, IntervalQuantity):
	# Convert the given interval for use in scanning the input files
	DeltaSeconds = 0
	DeltaMinutes = 0
	DeltaHours = 0
	ExpectedInputLinesPerInterval = 0
	if IntervalUnit == 'Second':
		if IntervalQuantity == 20:
			DeltaSeconds = 20
		elif IntervalQuantity == 30:
			DeltaSeconds = 30
		elif IntervalQuantity == 40:
			DeltaSeconds = 40
		else:
			IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Seconds')
	elif IntervalUnit == 'Minute':
		if IntervalQuantity == 1:
			DeltaMinutes = 1
		elif IntervalQuantity == 5:
			DeltaMinutes = 5
		elif IntervalQuantity == 10:
			DeltaMinutes = 10
		elif IntervalQuantity == 15:
			DeltaMinutes = 15
		elif IntervalQuantity ==30:
			DeltaMinutes = 30
		else:
			IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Minutes')
	elif IntervalUnit == 'Hour':
		if IntervalQuantity == 1:
			DeltaHours = 1
		elif IntervalQuantity == 2:
			DeltaHours = 2
		else:
			IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Hours')
	# Set up an file for averaging and another for sampling
	AveragingOutputFileName = f'SPX-{str(IntervalQuantity)}-{IntervalUnit}-A.csv'
	AveragingOutputFile = open(SharedVars.ScaledDataPath + '/' + AveragingOutputFileName, 'wt')
	SamplingOutputFileName = f'SPX-{str(IntervalQuantity)}-{IntervalUnit}-S.csv'
	SamplingOutputFile = open(SharedVars.ScaledDataPath + '/' + SamplingOutputFileName, 'wt')
	# InputFileNameList = sorted(os.listdir(SharedVars.FilteredDataPath))
	InputFileNameList = sorted(os.listdir(SharedVars.CheckedDataPath))
	# Traverse the list of input files
	for InputFileName in InputFileNameList:
		# InputFile = open(SharedVars.FilteredDataPath + '/' + InputFileName, 'rt')
		InputFile = open(SharedVars.CheckedDataPath + '/' + InputFileName, 'rt')
		# For each input file, set up the date strings for the output file lines
		InputFileNameParts = InputFileName.split('-')
		InputYear = int(InputFileNameParts[1])
		InputMonth = int(InputFileNameParts[2])
		InputDay = int(InputFileNameParts[3][0:2])

		# Averaging variables
		WaitingForSecondSamplePoint = True
		Accumulator = 0.0
		Count = 0
		SavedAccumulator = 0.0
		SavedCount = 0
		LaggingHour = 0
		LaggingMinute = 0
		LaggingSecond = 0

		# Start with the first time to be added to the output file
		OutputHour = 6
		OutputMinute = 30
		OutputSecond = 0
		# End when we get to 1:00
		EndHour = 13
		EndMinute = 0
		EndSecond = 0

		# Traverse the lines in the current input file
		for InputFileLine in InputFile:
			InputFileLineParts = InputFileLine.split(',')
			InputHour = int(InputFileLineParts[0])
			InputMinute = int(InputFileLineParts[1])
			InputSecond = int(InputFileLineParts[2])
			InputValue = float(InputFileLineParts[4])
			if OutputHour == 6 and OutputMinute == 30 and OutputSecond == 0:
				# This is the first input file entry - copy it straight across to both output files
				WriteToScaledOutputFile(AveragingOutputFile, InputYear, InputMonth, InputDay, OutputHour, OutputMinute, OutputSecond, InputValue)
				WriteToScaledOutputFile(SamplingOutputFile, InputYear, InputMonth, InputDay, OutputHour, OutputMinute, OutputSecond, InputValue)
				# Initialize interval recognition
				# TargetHour, TargetMinute, TargetSecond = IncrementOutputTime(OutputHour, OutputMinute, OutputSecond, DeltaHours, DeltaMinutes, DeltaSeconds)
				OutputHour, OutputMinute, OutputSecond = IncrementOutputTime(OutputHour, OutputMinute, OutputSecond, DeltaHours, DeltaMinutes, DeltaSeconds)
				# Initialize averaging
				Accumulator = 0.0
				Count = 0
				SavedAccumulator = 0.0
				SavedCount = 0
			else:
				# This is beyond the first entry
				TargetTimeReached = TimesAreEqual(InputHour, InputMinute, InputSecond, OutputHour, OutputMinute, OutputSecond)
				EndOfInputDayReached = TimesAreEqual(InputHour, InputMinute, InputSecond, EndHour, EndMinute, EndSecond)
				if TargetTimeReached or EndOfInputDayReached:
					# This input file entry falls on (well.... close enough to) the next target time or the end of the input day so
					#  the sampling output file gets written
					if not EndOfInputDayReached:
						WriteToScaledOutputFile(SamplingOutputFile, InputYear, InputMonth, InputDay, OutputHour, OutputMinute, OutputSecond, InputValue)
					# The averaging output file wants to write the average of the last TWO intervals out as the value for the PREVIOUS time
					#  ... so we have to skip the past the first sampling point before we start writing out average values
					if WaitingForSecondSamplePoint:
						# The lagging average handling means we have to skip past one output average write
						WaitingForSecondSamplePoint = False
					else:
						# We're at least up to the third time point in the input file so we write the average for the previous time point into the output file
						AverageValue = (Accumulator + SavedAccumulator) / (Count + SavedCount)
						WriteToScaledOutputFile(AveragingOutputFile, InputYear, InputMonth, InputDay, LaggingHour, LaggingMinute, LaggingSecond, AverageValue)
					# Is this the last sample point (1:00)?
					if EndOfInputDayReached:
						# # This is the last time point so....
						# # 1) Write the final entry into both the  files as just the plain value at 1:00
						WriteToScaledOutputFile(AveragingOutputFile, InputYear, InputMonth, InputDay, EndHour, EndMinute, EndSecond, InputValue)
						WriteToScaledOutputFile(SamplingOutputFile, InputYear, InputMonth, InputDay, EndHour, EndMinute, EndSecond, InputValue)
						# # 2) Move on to the next input file (hmmmm, sort of redundant to the file's eof... not entirely sure how this will interact with the above "for InputFileLine")
						break
					else:
						# update things for processing the next interval
						LaggingHour = OutputHour
						LaggingMinute = OutputMinute
						LaggingSecond = OutputSecond
						OutputHour, OutputMinute, OutputSecond = IncrementOutputTime(OutputHour, OutputMinute, OutputSecond, DeltaHours, DeltaMinutes, DeltaSeconds)
						SavedAccumulator = Accumulator + InputValue
						SavedCount = Count + 1
						Accumulator = 0.0
						Count = 0
				else:
					# This input file entry falls between the times that are to be included in the output file
					# ??? Possible error if we've passed the target time without coming close enough to it.
					if Time1IsAfterTime2(InputHour, InputMinute, InputSecond, OutputHour, OutputMinute, OutputSecond):
						# !!!! We apparently missed our target time
						IbViewUtilities.AddLineToTextWindow(f'Missed target {InputYear}-{InputMonth}-{InputDay}@{OutputHour}:{OutputMinute}:{OutputSecond}')
					else:
						# This is one of those "in-between" input entries
						Accumulator += InputValue
						Count += 1
		InputFile.close()
	AveragingOutputFile.close()
	SamplingOutputFile.close()

def WriteToScaledOutputFile(oFile, oYear, oMonth, oDay, oHour, oMinute, oSecond, oValue):
	print(f'{oYear}, {oMonth}, {oDay}, {oHour}, {oMinute}, {oSecond}, {oValue:.2f}', file=oFile)

def IncrementOutputTime(OutputHour, OutputMinute, OutputSecond, DeltaHours, DeltaMinutes, DeltaSeconds):
	WorkingHour = OutputHour
	WorkingMinute = OutputMinute
	WorkingSecond = OutputSecond
	WorkingSecond += DeltaSeconds
	if WorkingSecond > 59:
		WorkingMinute += 1
		WorkingSecond -= 60
	WorkingMinute += DeltaMinutes
	if WorkingMinute > 59:
		WorkingHour += 1
		WorkingMinute -= 60
	WorkingHour += DeltaHours
	return WorkingHour, WorkingMinute, WorkingSecond

def TimesAreEqual(Hour1, Minute1, Second1, Hour2, Minute2, Second2):
	# Return True if there is 5 seconds or less difference between the two times provided
	TotalSeconds1 = 3600 * Hour1 + 60 * Minute1 + Second1
	TotalSeconds2 = 3600 * Hour2 + 60 * Minute2 + Second2
	if abs(TotalSeconds1 - TotalSeconds2) <= 5:
		return True
	else:
		return False

def Time1IsAfterTime2(Hour1, Minute1, Second1, Hour2, Minute2, Second2):
	# Return True if time1 is more than 5 seconds later than time2
	TotalSeconds1 = 3600 * Hour1 + 60 * Minute1 + Second1
	TotalSeconds2 = 3600 * Hour2 + 60 * Minute2 + Second2
	if TotalSeconds1 - TotalSeconds2 > 5:
		return True
	else:
		return False

def ShapeAllScaledData():
	InputFileNameList = sorted(os.listdir(SharedVars.ScaledDataPath))
	# Traverse the list of input files
	for InputFileName in InputFileNameList:
		WriteOutput = True
		if InputFileName[-4:] != '.csv':
			print(f'Unexpected input file not ending in .csf: {InputFileName}')
		else:
			InputFileNameParts = InputFileName[:-4].split('-')
			if InputFileNameParts[0] != 'SPX':
				print(f'Unexpected input file not starting with SPX: {InputFileName}')
			else:
				InputFile = open(SharedVars.ScaledDataPath + '/' + InputFileName, 'rt')
				IntervalQuantity = int(InputFileNameParts[1])
				IntervalUnit = InputFileNameParts[2]
				ASLetter = InputFileNameParts[3]
				# Convert the given interval for use in scanning the input files
				NumberOfInputLinesPerDay = 0
				NumberOfInputLinesTo11AM = 0
				CheckHour = 0
				CheckMinute = 0
				if IntervalUnit == 'Second':
					WriteOutput = False
					if IntervalQuantity == 20:
						NumberOfInputLinesPerDay = 1171
						NumberOfInputLinesTo11AM = 811
						CheckHour = 11
						CheckMinute = 0
					elif IntervalQuantity == 30:
						NumberOfInputLinesPerDay = 781
						NumberOfInputLinesTo11AM = 541
						CheckHour = 11
						CheckMinute = 0
					elif IntervalQuantity == 40:
						NumberOfInputLinesPerDay = 586
						NumberOfInputLinesTo11AM = 406
						CheckHour = 11
						CheckMinute = 0
					else:
						IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Seconds')
				elif IntervalUnit == 'Minute':
					if IntervalQuantity == 1:
						WriteOutput = False
						NumberOfInputLinesPerDay = 391
						NumberOfInputLinesTo11AM = 271
						CheckHour = 11
						CheckMinute = 0
					elif IntervalQuantity == 5:
						WriteOutput = False
						NumberOfInputLinesPerDay = 79
						NumberOfInputLinesTo11AM = 55
						CheckHour = 11
						CheckMinute = 0
					elif IntervalQuantity == 10:
						# WriteOutput = False
						NumberOfInputLinesPerDay = 40
						NumberOfInputLinesTo11AM = 28
						CheckHour = 11
						CheckMinute = 0
					elif IntervalQuantity == 15:
						# WriteOutput = False
						NumberOfInputLinesPerDay = 27
						NumberOfInputLinesTo11AM = 19
						CheckHour = 11
						CheckMinute = 0
					elif IntervalQuantity ==30:
						NumberOfInputLinesPerDay = 14
						NumberOfInputLinesTo11AM = 10
						CheckHour = 11
						CheckMinute = 0
					else:
						IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Minutes')
				elif IntervalUnit == 'Hour':
					if IntervalQuantity == 1:
						NumberOfInputLinesPerDay = 8
						NumberOfInputLinesTo11AM = 5
						CheckHour = 10
						CheckMinute = 30
					elif IntervalQuantity == 2:
						NumberOfInputLinesPerDay = 5
						NumberOfInputLinesTo11AM = 3
						CheckHour = 10
						CheckMinute = 30
					else:
						IbViewUtilities.ErrorExit(f'Unexpected scale interval: {IntervalQuantity} Hours')
				if WriteOutput:
					# How many elements will go into a sample vector?
					SampleVectorLength = (SharedVars.NumberOfDaysInASample - 1) * NumberOfInputLinesPerDay + NumberOfInputLinesTo11AM
					# How many input lines will be skipped from the end of the sample vector (11:00 today) to the corresponding today label value (1:00 today)
					NumberOfInputLinesFrom11AMToTodayClose = NumberOfInputLinesPerDay - NumberOfInputLinesTo11AM
					# How many input lines will be skipped from the end of the sample vector (11:00 today) to the corresponding tomorrow label value (1:00 tomorrow)
					NumberOfInputLinesFrom11AMToTomorrowClose = 2 * NumberOfInputLinesPerDay - NumberOfInputLinesTo11AM
					# How many input lines to encompass a sample vector all the way to the furthest corresponding label value (tomorrow close)?
					# ... 20 days + 1 more day to get to the desired "tomorrow close"
					NumberOfInputLinesInCompleteOutputBuffer = (SharedVars.NumberOfDaysInASample + 1) * NumberOfInputLinesPerDay
					# A buffer to hold all the sequential values from the first in an input vector through the corresponding label value
					GenericSampleOutputFileName = f'SPX-{IntervalQuantity}-{IntervalUnit}-{ASLetter}-G-S-{SampleVectorLength}.csv'
					GenericLabelOutputFileName = f'SPX-{IntervalQuantity}-{IntervalUnit}-{ASLetter}-G-L-{SampleVectorLength}.csv'
					SemiGenericSampleOutputFileName = f'SPX-{IntervalQuantity}-{IntervalUnit}-{ASLetter}-g-S-{SampleVectorLength}.csv'
					SemiGenericLabelOutputFileName = f'SPX-{IntervalQuantity}-{IntervalUnit}-{ASLetter}-g-L-{SampleVectorLength}.csv'
					ParticularSampleOutputFileName = f'SPX-{IntervalQuantity}-{IntervalUnit}-{ASLetter}-P-S-{SampleVectorLength}.csv'
					ParticularLabelOutputFileName = f'SPX-{IntervalQuantity}-{IntervalUnit}-{ASLetter}-P-L-{SampleVectorLength}.csv'
					GenericSampleOutputFile = open(SharedVars.ShapedDataPath + '/' + GenericSampleOutputFileName, 'wt')
					GenericLabelOutputFile = open(SharedVars.ShapedDataPath + '/' + GenericLabelOutputFileName, 'wt')
					SemiGenericSampleOutputFile = open(SharedVars.ShapedDataPath + '/' + SemiGenericSampleOutputFileName, 'wt')
					SemiGenericLabelOutputFile = open(SharedVars.ShapedDataPath + '/' + SemiGenericLabelOutputFileName, 'wt')
					ParticularSampleOutputFile = open(SharedVars.ShapedDataPath + '/' + ParticularSampleOutputFileName, 'wt')
					ParticularLabelOutputFile = open(SharedVars.ShapedDataPath + '/' + ParticularLabelOutputFileName, 'wt')
					# Pandas read_csv is pretty cranky if there's no first line with column labels...
					SampleFileColumnNames = ''
					for i in range (SampleVectorLength - 1):
						SampleFileColumnNames += f't({str(i - SampleVectorLength + 1)}), '
					SampleFileColumnNames += 't(0)'
					print(f'{SampleFileColumnNames}',file=GenericSampleOutputFile)
					print(f'{SampleFileColumnNames}',file=SemiGenericSampleOutputFile)
					print(f'{SampleFileColumnNames}',file=ParticularSampleOutputFile)
					LabelFileColumnNames = '11 oclock,Today close,Tomorrow close,Today 2,Tomorrow 2,Today 3,Tomorrow 3,Today 5,Tomorrow 5'
					print(f'{LabelFileColumnNames}',file=GenericLabelOutputFile)
					print(f'{LabelFileColumnNames}',file=SemiGenericLabelOutputFile)
					print(f'{LabelFileColumnNames}',file=ParticularLabelOutputFile)
					OutputValueStorage = []
					InputLineCounter = 0
					IbViewUtilities.AddLineToTextWindow(f'Shaping {IntervalQuantity} {IntervalUnit} {ASLetter}')
					SharedVars.GuiWindow.update()
					for InputFileLine in InputFile:
						InputLineCounter += 1
						InputLineParts = InputFileLine.rstrip('\n').split(',')
						InputLineYear = InputLineParts[0]
						InputLineMonth = InputLineParts[1]
						InputLineDay = InputLineParts[2]
						InputLineHour = InputLineParts[3]
						InputLineMinute = InputLineParts[4]
						InputLineSecond = InputLineParts[5]
						InputLineValueString = InputLineParts[6]
						# add the next input value to the end of the buffer
						OutputValueStorage.append(InputLineValueString)
						if len(OutputValueStorage) == NumberOfInputLinesInCompleteOutputBuffer:
							# There are enough values in the buffer to make an output sample and label so...
							# 1) Build a sample vector and label set
							#  A) Label(s) are four elements: the tomorrow close value plus three variations of proper integer labels
							ElevenOclockValueString = OutputValueStorage[SampleVectorLength - 1].strip()
							TodayCloseValueString = OutputValueStorage[SampleVectorLength + NumberOfInputLinesFrom11AMToTodayClose - 1].strip()
							TomorrowCloseValueString = OutputValueStorage[-1].strip()
							ElevenOclockValue = float(ElevenOclockValueString)
							TodayCloseValue = float(TodayCloseValueString)
							TomorrowCloseValue = float(TomorrowCloseValueString)
							FiveDollarRailBelowElevenOclockValue = float( ( math.floor(ElevenOclockValue) // 5 ) * 5 )
							FiveDollarRailAboveElevenOclockValue = FiveDollarRailBelowElevenOclockValue + 5.0
							TenDollarRailBelowElevenOclockValue = FiveDollarRailBelowElevenOclockValue - 5.0
							TenDollarRailAboveElevenOclockValue = FiveDollarRailAboveElevenOclockValue + 5.0
							# Figure the simple binary "above/below" labels
							if TodayCloseValue > ElevenOclockValue:
								Label2TodayString = '1'
							else:
								Label2TodayString = '-1'
							if TomorrowCloseValue > ElevenOclockValue:
								Label2TomorrowString = '1'
							else:
								Label2TomorrowString = '-1'
							# Figure the labels for "above/below/within" the $5 band
							if TodayCloseValue > FiveDollarRailAboveElevenOclockValue:
								Label3TodayString = '1'
								Label5TodayString = '1'
							elif TodayCloseValue < FiveDollarRailBelowElevenOclockValue:
								Label3TodayString = '-1'
								Label5TodayString = '-1'
							else:
								Label3TodayString = '0'
								Label5TodayString = '0'
							if TomorrowCloseValue > FiveDollarRailAboveElevenOclockValue:
								Label3TomorrowString = '1'
								Label5TomorrowString = '1'
							elif TomorrowCloseValue < FiveDollarRailBelowElevenOclockValue:
								Label3TomorrowString = '-1'
								Label5TomorrowString = '-1'
							else:
								Label3TomorrowString = '0'
								Label5TomorrowString = '0'
							# Check if the above/below is more than $5 above or below the $5 band
							if TodayCloseValue > TenDollarRailAboveElevenOclockValue:
								Label5TodayString = '2'
							elif TodayCloseValue < TenDollarRailBelowElevenOclockValue:
								Label5TodayString = '-2'
							else:
								pass
							if TomorrowCloseValue > TenDollarRailAboveElevenOclockValue:
								Label5TomorrowString = '2'
							elif TomorrowCloseValue < TenDollarRailBelowElevenOclockValue:
								Label5TomorrowString = '-2'
							else:
								pass
							OutputLabelString = f'{ElevenOclockValueString},{TodayCloseValueString},{TomorrowCloseValueString},{Label2TodayString},{Label2TomorrowString},{Label3TodayString},{Label3TomorrowString},{Label5TodayString},{Label5TomorrowString}'
							#  B) Sample vector is values for previous 19 days plus 20th day values up to 11:00
							OutputSampleString = ''
							for SampleIndex in range(SampleVectorLength - 1):
								OutputSampleString += OutputValueStorage[SampleIndex] + ', '
							OutputSampleString += OutputValueStorage[SampleVectorLength - 1]
							# 2) Write the sample and label to their output files
							# Write ALL samples and labels to the generic files
							print(f'{OutputSampleString}', file = GenericSampleOutputFile)
							print(f'{OutputLabelString}', file = GenericLabelOutputFile)
							# If the label time is 1:00 PM then this is a semi-generic data set so write it to those files, too
							if int(InputLineHour) == 13 and int(InputLineMinute) == 0:
								print(f'{OutputSampleString}', file = SemiGenericSampleOutputFile)
								print(f'{OutputLabelString}', file = SemiGenericLabelOutputFile)
								# If this is a semi-generic data set AND the label value is from a date that's an SPX expiration date, then it's also "particular"
								if IbViewUtilities.DateIsAnSpxExpirationDay(datetime.date(int(InputLineYear), int(InputLineMonth), int(InputLineDay))):
									print(f'{OutputSampleString}', file = ParticularSampleOutputFile)
									print(f'{OutputLabelString}', file = ParticularLabelOutputFile)
							# Remove the first element from the beginning to make room for the next one at the end
							del OutputValueStorage[0]
					GenericSampleOutputFile.close()
					GenericLabelOutputFile.close()
					SemiGenericSampleOutputFile.close()
					SemiGenericLabelOutputFile.close()
					ParticularSampleOutputFile.close()
					ParticularLabelOutputFile.close()
				InputFile.close()
