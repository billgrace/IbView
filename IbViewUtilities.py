import os
import datetime
import SharedVars
import IbViewEnums
import IbViewClasses
import IbViewGui

# Accept a string that was utf-8-encoded from a byte array and return the byte array from which the string was encoded
def DecodeStringToBytes(String):
	ReturnBytes = bytearray()
	DecodeCounter = 0
	DecodeValue = 0
	CharNumber = 0
	CharValue = 0
	for Char in String:
		CharValue = Char
		CharNumber += 1
		if DecodeCounter == 0:
			# DecodeCounter == 0 means we're not currently processing an escape sequence
			if ord(Char) == 92:
				# This character is a backslash so it's the start of an escape sequence
				DecodeCounter = 1
				DecodeValue = 0
			else:
				# this char is just a printable ASCII char so add it to the byte array
				ReturnBytes.append(ord(Char))
		elif DecodeCounter == 1:
			# DecodeCounter == 1 means
			# this is the character following a backslash....
			# Is it an escaped binary value??
			if ord(Char) == 120:
				# it's the x of '\xnn' so ignore it and move on to collect the two hex digits following
				DecodeCounter = 2
			# Is it an escaped ASCII control code??
			elif ord(Char) == 97:
				# it's the a of a 'Bell' ('\a') so declare an ASCII BEL byte
				ReturnBytes.append(7)
				DecodeCounter = 0
			elif ord(Char) == 98:
				# it's the b of a backspace ('\b') so declare an ASCII BS byte
				ReturnBytes.append(8)
				DecodeCounter = 0
			elif ord(Char) == 116:
				# it's the t of a tab ('\t') so declare an ASCII TAB byte
				ReturnBytes.append(9)
				DecodeCounter = 0
			elif ord(Char) == 110:
				# it's the n of a newline ('\n') so declare an ASCII LF byte
				ReturnBytes.append(10)
				DecodeCounter = 0
			elif ord(Char) == 118:
				# it's the v of a vertical tab ('\v') so declare an ASCII VT byte
				ReturnBytes.append(11)
				DecodeCounter = 0
			elif ord(Char) == 102:
				# it's the f of a form feed ('\f') so declare an ASCII FF byte
				ReturnBytes.append(12)
				DecodeCounter = 0
			elif ord(Char) == 114:
				# it's the r of a carriage return ('\r') so declare an ASCII CR byte
				ReturnBytes.append(13)
				DecodeCounter = 0
			# Is it an escaped quote or backslash??
			elif ord(Char) == 34:
				# it's a double quote
				ReturnBytes.append(34)
				DecodeCounter = 0
			elif ord(Char) == 39:
				# it's a single quote
				ReturnBytes.append(39)
				DecodeCounter = 0
			elif ord(Char) == 92:
				# it's a second backslash so the two of them amount to an original backslash byte
				ReturnBytes.append(92)
				DecodeCounter = 0
			else:
				# There shouldn't be any other character following a backslash.
				print(f'Bad escape sequence: backslash {Char}')
				ReturnBytes.append(92)
				ReturnBytes.append(ord(Char))
				DecodeCounter = 0
		elif DecodeCounter == 2:
			# this char is the MSB of the encoded value
			DecodeValue = 16 * IntegerHexValue(Char)
			DecodeCounter = 3
		else:
			# this char is the LSB of the encoded value
			DecodeValue += IntegerHexValue(Char)
			ReturnBytes.append(DecodeValue)
			DecodeCounter = 0
	if DecodeCounter == 1:
		# There should never be a backslash as the last character....
		print('There was an un-accompanied backslash at the end of the string.')
	return ReturnBytes

# This version does as good a job as I can manage for the poorly-encoded data before June 15, 2018
def DecodeStringToBytesPreJune15_2018(String):
	ReturnBytes = bytearray()
	DecodeCounter = 0
	DecodeValue = 0
	CharNumber = 0
	CharValue = 0
	for Char in String:
		CharValue = Char
		CharNumber += 1
		if DecodeCounter == 0:
			# DecodeCounter == 0 means we're not currently processing an escape sequence
			if ord(Char) == 92:
				# This character is a backslash so it's potentially the start of an escape sequence
				DecodeCounter = 1
				DecodeValue = 0
			else:
				# this char is just a printable ASCII char so add it to the byte array
				ReturnBytes.append(ord(Char))
		elif DecodeCounter == 1:
			# DecodeCounter == 1 means
			# this is the character following a backslash....
			# Is it an escaped ASCII control code??
			if ord(Char) == 120:
				# it's the x of '\xnn' so ignore it and move on to collect the two hex digits following
				DecodeCounter = 2
			elif ord(Char) == 97:
				# it's the a of a 'Bell' ('\a') so declare an ASCII BEL byte
				ReturnBytes.append(7)
				DecodeCounter = 0
			elif ord(Char) == 98:
				# it's the b of a backspace ('\b') so declare an ASCII BS byte
				ReturnBytes.append(8)
				DecodeCounter = 0
			elif ord(Char) == 116:
				# it's the t of a tab ('\t') so declare an ASCII TAB byte
				ReturnBytes.append(9)
				DecodeCounter = 0
			elif ord(Char) == 110:
				# it's the n of a newline ('\n') so declare an ASCII LF byte
				ReturnBytes.append(10)
				DecodeCounter = 0
			elif ord(Char) == 118:
				# it's the v of a vertical tab ('\v') so declare an ASCII VT byte
				ReturnBytes.append(11)
				DecodeCounter = 0
			elif ord(Char) == 102:
				# it's the f of a form feed ('\f') so declare an ASCII FF byte
				ReturnBytes.append(12)
				DecodeCounter = 0
			elif ord(Char) == 114:
				# it's the r of a carriage return ('\r') so declare an ASCII CR byte
				ReturnBytes.append(13)
				DecodeCounter = 0
			elif ord(Char) == 92:
				# it's another backslash so the first one is just a backslash character and we
				# shift our possible-escape-sequence processing to this second one
				ReturnBytes.append(92)
				DecodeCounter = 1
			else:
				# it's not one of our escape sequences so it must be just a backslash followed by some other character
				ReturnBytes.append(92)
				ReturnBytes.append(ord(Char))
				DecodeCounter = 0
		elif DecodeCounter == 2:
			# this char is the MSB of the encoded value
			DecodeValue = 16 * IntegerHexValue(Char)
			DecodeCounter = 3
		else:
			# this char is the LSB of the encoded value
			DecodeValue += IntegerHexValue(Char)
			ReturnBytes.append(DecodeValue)
			DecodeCounter = 0
	if DecodeCounter == 1:
		# This string ends with a backslash so add it to the byte array equivalent we've built
		ReturnBytes.append(ord('\\'))
	return ReturnBytes

def IntegerHexValue(Char):
	if Char == '0':
		return 0
	elif Char == '1':
		return 1
	elif Char == '2':
		return 2
	elif Char == '3':
		return 3
	elif Char == '4':
		return 4
	elif Char == '5':
		return 5
	elif Char == '6':
		return 6
	elif Char == '7':
		return 7
	elif Char == '8':
		return 8
	elif Char == '9':
		return 9
	elif Char == 'a':
		return 10
	elif Char == 'b':
		return 11
	elif Char == 'c':
		return 12
	elif Char == 'd':
		return 13
	elif Char == 'e':
		return 14
	elif Char == 'f':
		return 15
	elif Char == 'A':
		return 10
	elif Char == 'B':
		return 11
	elif Char == 'C':
		return 12
	elif Char == 'D':
		return 13
	elif Char == 'E':
		return 14
	elif Char == 'F':
		return 15
	else:
		return -1

def StringFormatDollars(FloatAmount):
	if FloatAmount > 999999999999.0:
		return '**++**'
	if FloatAmount < -999999999999.0:
		return '**--**'
	return '${:,.2f}'.format(FloatAmount)

def StringFormatGreek(FloatAmount):
	if FloatAmount > 1000:
		return '**++**'
	if FloatAmount < -1000:
		return '**--**'
	return '{:,.4f}'.format(FloatAmount)

def StringFormatTimestamp(Timestamp):
	return '{Hour:02d}:{Minute:02d}:{Second:02d}.{Millisecond:03d}'.format(**Timestamp)

def FormatDateShortMonth(date):
	return f'{date.strftime("%b %-d, %Y")}'

def CompareDates(Date1, Date2):
	if Date1.year < Date2.year:
		return IbViewEnums.DateComparisonResult['FirstIsBeforeSecond']
	elif Date1.year > Date2.year:
		return IbViewEnums.DateComparisonResult['FirstIsAfterSecond']
	else:
		if Date1.month < Date2.month:
			return IbViewEnums.DateComparisonResult['FirstIsBeforeSecond']
		elif Date1.month > Date2.month:
			return IbViewEnums.DateComparisonResult['FirstIsAfterSecond']
		else:
			if Date1.day < Date2.day:
				return IbViewEnums.DateComparisonResult['FirstIsBeforeSecond']
			elif Date1.day > Date2.day:
				return IbViewEnums.DateComparisonResult['FirstIsAfterSecond']
			else:
				return IbViewEnums.DateComparisonResult['DatesAreEqual']

def LogError(message):
	ErrorTimestamp = datetime.datetime.now()
	ErrorTimeString = '{0:%A} {0:%B} {0:%d}, {0:%Y} @ {0:%I:%M%p} '.format(ErrorTimestamp)
	FormattedErrorString = ErrorTimeString + message
	IbViewGui.GuiShowDevelopmentMessage(FormattedErrorString)
	print(FormattedErrorString)

TradingDates2018 = []
TradingDates2019 = []
TradingDates2020 = []
SpxExpirationDates2018 = []
SpxExpirationDates2019 = []
SpxExpirationDates2020 = []
TradingDates2018.append("zero place holder since datetime.month returns 1-12")
TradingDates2018.append("2,3,4,5,8,9,10,11,12,16,17,18,19,22,23,24,25,26,29,30,31")
TradingDates2018.append("1,2,5,6,7,8,9,12,13,14,15,16,19,20,21,22,23,26,27,28")
TradingDates2018.append("1,2,5,6,7,8,9,12,13,14,15,16,19,20,21,22,23,26,27,28,29")
TradingDates2018.append("2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30")
TradingDates2018.append("1,2,3,4,7,8,9,10,11,14,15,16,17,18,21,22,23,24,25,29,30,31")
TradingDates2018.append("1,4,5,6,7,8,11,12,13,14,15,18,19,20,21,22,25,26,27,28,29")
TradingDates2018.append("2,3,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30,31")
TradingDates2018.append("1,2,3,6,7,8,9,10,13,14,15,16,17,20,21,22,23,24,27,28,29,30,31")
TradingDates2018.append("4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28")
TradingDates2018.append("1,2,3,4,5,8,9,10,11,12,15,16,17,18,19,22,23,24,25,26,29,30,31")
TradingDates2018.append("1,2,5,6,7,8,9,12,13,14,15,16,19,20,21,23,26,27,28,29,30")
TradingDates2018.append("3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,26,27,28,31")
SpxExpirationDates2018.append("zero place holder since datetime.month returns 1-12")
SpxExpirationDates2018.append("3,5,8,10,12,17,19,22,24,26,29,31")
SpxExpirationDates2018.append("2,5,7,9,12,14,16,21,23,26,28")
SpxExpirationDates2018.append("2,5,7,9,12,14,16,19,21,23,26,28")
SpxExpirationDates2018.append("2,4,6,9,11,13,16,18,29,23,25,27,30")
SpxExpirationDates2018.append("2,4,7,9,11,14,16,18,21,23,25,30")
SpxExpirationDates2018.append("1,4,6,8,11,13,15,18,20,22,25,27,29")
SpxExpirationDates2018.append("2,6,9,11,13,16,18,20,23,255,27,30")
SpxExpirationDates2018.append("1,3,6,8,10,13,15,17,20,22,24,27,29,31")
SpxExpirationDates2018.append("5,7,10,12,14,17,19,21,24,26,28")
SpxExpirationDates2018.append("1,3,5,8,10,12,15,17,19,22,24,26,29,31")
SpxExpirationDates2018.append("2,5,7,9,12,14,16,19,21,23,26,28,30")
SpxExpirationDates2018.append("3,5,7,10,12,14,17,19,21,24,26,28,31")
TradingDates2019.append("zero place holder since datetime.month returns 1-12")
TradingDates2019.append("2,3,4,7,8,9,10,11,15,16,17,18,21,22,23,24,25,28,29,30,31")
TradingDates2019.append("1,4,5,6,7,8,11,12,13,14,15,19,20,21,22,25,26,27,28")
TradingDates2019.append("1,4,5,6,7,8,11,12,13,14,15,18,19,20,21,22,25,26,27,28,29")
TradingDates2019.append("1,2,3,4,5,8,9,10,11,12,15,16,17,18,22,23,24,25,26,29,30")
TradingDates2019.append("1,2,3,6,7,8,9,10,13,14,15,16,17,20,21,22,23,24,28,29,30,31")
TradingDates2019.append("3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28")
TradingDates2019.append("1,2,3,5,8,9,10,11,12,15,16,17,18,19,22,23,24,25,26,29,30,31")
TradingDates2019.append("1,2,5,6,7,8,9,12,13,14,15,16,19,20,21,22,23,26,27,28,29,30")
TradingDates2019.append("3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30")
TradingDates2019.append("1,2,3,4,7,8,9,10,11,14,15,16,17,18,21,22,23,24,25,28,29,30,31")
TradingDates2019.append("1,4,5,6,7,8,11,12,13,14,15,18,19,20,21,22,25,26,27,29")
TradingDates2019.append("2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,26,27,30,31")
SpxExpirationDates2019.append("zero place holder since datetime.month returns 1-12")
SpxExpirationDates2019.append("2,4,7,9,11,16,18,21,23,25,28,30")
SpxExpirationDates2019.append("1,4,6,8,11,13,15,20,22,25,27")
SpxExpirationDates2019.append("1,4,6,8,11,13,15,18,20,22,25,27,29")
SpxExpirationDates2019.append("1,3,5,8,10,12,15,17,22,24,26,29")
SpxExpirationDates2019.append("1,3,6,8,10,13,15,17,20,22,24,29,31")
SpxExpirationDates2019.append("3,5,7,10,12,14,17,19,21,24,26,28")
SpxExpirationDates2019.append("1,3,5,8,10,12,15,17,19,22,24,26,29,31")
SpxExpirationDates2019.append("2,5,7,9,12,14,16,19,21,13,26,28,30")
SpxExpirationDates2019.append("2,4,6,9,11,13,16,18,20,23,25,27,30")
SpxExpirationDates2019.append("2,4,7,9,11,14,16,18,21,23,25,28,30")
SpxExpirationDates2019.append("1,4,6,8,11,13,15,18,20,22,25,27,29")
SpxExpirationDates2019.append("2,4,6,9,11,13,16,18,20,23,27,30")
TradingDates2020.append("zero place holder since datetime.month returns 1-12")
TradingDates2020.append("2,3,6,7,8,9,10,13,14,15,16,17,21,22,23,24,27,28,29,30,31")
TradingDates2020.append("3,4,5,6,7,10,11,12,13,14,18,19,20,21,24,25,26,27,28")
TradingDates2020.append("2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30,31")
TradingDates2020.append("1,2,36,7,8,9,13,14,15,16,17,20,21,22,23,24,27,28,29,30")
TradingDates2020.append("1,4,5,6,7,8,11,12,13,14,15,18,19,20,21,22,26,27,28,29")
TradingDates2020.append("1,2,3,4,5,8,9,10,11,12,15,16,17,18,19,22,23,24,25,26,29,30")
TradingDates2020.append("1,2,6,7,8,9,10,13,14,15,16,17,20,21,22,23,24,27,28,29,30,31")
TradingDates2020.append("3,4,5,6,7,10,11,12,13,14,17,18,19,20,21,24,25,26,27,28,31")
TradingDates2020.append("1,2,3,4,8,9,10,11,14,15,16,17,18,21,22,23,24,25,28,29,30")
TradingDates2020.append("1,2,5,6,7,8,9,12,13,14,15,16,19,20,21,22,23,26,27,28,29,30")
TradingDates2020.append("2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,27,30")
TradingDates2020.append("1,2,3,4,7,8,9,10,11,14,15,16,17,18,21,22,23,24,28,29,30,31")
SpxExpirationDates2020.append("zero place holder since datetime.month returns 1-12")
SpxExpirationDates2020.append("3,6,8,10,13,15,17,22,24,27,29,31")
SpxExpirationDates2020.append("3,5,7,10,12,14,19,21,24,26,28")
SpxExpirationDates2020.append("2,4,6,9,11,13,16,18,20,23,25,27,30")
SpxExpirationDates2020.append("1,3,6,8,13,15,17,20,22,24,27,29")
SpxExpirationDates2020.append("1,4,6,8,11,13,15,18,20,22,27,29")
SpxExpirationDates2020.append("1,3,5,8,10,12,15,17,19,22,24,26,29")
SpxExpirationDates2020.append("1,6,8,10,13,15,17,20,22,24,27,29,31")
SpxExpirationDates2020.append("3,5,7,10,12,14,17,19,21,24,26,28,31")
SpxExpirationDates2020.append("2,4,9,11,14,16,18,21,23,25,28,30")
SpxExpirationDates2020.append("2,5,7,9,14,16,19,21,23,26,28,30")
SpxExpirationDates2020.append("2,4,6,9,11,13,16,18,20,23,25,27,30")
SpxExpirationDates2020.append("2,4,7,9,11,14,16,18,21,23,28,30")

def DateIsATradingDay(date):
	returnValue = False
	stringArrayIndex = date.month
	todayDayInteger = date.day
	if date.year == 2018:
		dayStrings = TradingDates2018[stringArrayIndex].split(',')
	elif date.year == 2019:
		dayStrings = TradingDates2019[stringArrayIndex].split(',')
	elif date.year == 2020:
		dayStrings = TradingDates2020[stringArrayIndex].split(',')
	else:
		ErrorExit(f'Bad year in DateIsATradingDay: {date.year}')
	for dayString in dayStrings:
		if (todayDayInteger == int(dayString)):
			returnValue = True
			break
	return returnValue

def DateIsAnSpxExpirationDay(date):
	returnValue = False
	stringArrayIndex = date.month
	todayDayInteger = date.day
	if date.year == 2018:
		dayStrings = SpxExpirationDates2018[stringArrayIndex].split(',')
	elif date.year == 2019:
		dayStrings = SpxExpirationDates2019[stringArrayIndex].split(',')
	elif date.year == 2020:
		dayStrings = SpxExpirationDates2020[stringArrayIndex].split(',')
	else:
		ErrorExit(f'Bad year in DateIsATradingDay: {date.year}')
	for dayString in dayStrings:
		if (todayDayInteger == int(dayString)):
			returnValue = True
			break
	return returnValue

def DateIsAlreadySifted(date):
    returnValue = False
    FileNameDateFormat = f"{date.year:4}-{date.month:02}-{date.day:02}.csv"
    SiftedDataFileDirectoryList = os.listdir(SharedVars.SiftedDataPath)
    for SiftedDataFileName in SiftedDataFileDirectoryList:
        if FileNameDateFormat == SiftedDataFileName[-14:]:
            returnValue = True
            break
    return returnValue

def DateIsAlreadyFiltered(date):
    returnValue = False
    FileNameDateFormat = f"{date.year:4}-{date.month:02}-{date.day:02}.csv"
    FilteredDataFileDirectoryList = os.listdir(SharedVars.FilteredDataPath)
    for FilteredDataFileName in FilteredDataFileDirectoryList:
        if FileNameDateFormat == FilteredDataFileName[-14:]:
            returnValue = True
            break
    return returnValue

def DateIsAlreadyChecked(date):
    returnValue = False
    FileNameDateFormat = f"{date.year:4}-{date.month:02}-{date.day:02}.csv"
    CheckedDataFileDirectoryList = os.listdir(SharedVars.CheckedDataPath)
    for CheckedDataFileName in CheckedDataFileDirectoryList:
        if FileNameDateFormat == CheckedDataFileName[-14:]:
            returnValue = True
            break
    return returnValue

def EmptyTextWindow():
	SharedVars.GuiTextWindow.delete('1.0', 'end')

def AddLineToTextWindow(text):
	SharedVars.GuiTextWindow.insert('end', text + '\n')
	SharedVars.GuiTextWindow.see('end')

def AddTextToTextWindow(text):
	SharedVars.GuiTextWindow.insert('end', text + ' ')
	SharedVars.GuiTextWindow.see('end')

def ErrorExit(message):
	print(message)
	exit()
	