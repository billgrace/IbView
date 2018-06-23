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

def CompareDates(Date1, Date2):
	if Date1['year'] < Date2['year']:
		return IbViewEnums.DateComparisonResult['FirstIsBeforeSecond']
	elif Date1['year'] > Date2['year']:
		return IbViewEnums.DateComparisonResult['FirstIsAfterSecond']
	else:
		if Date1['month'] < Date2['month']:
			return IbViewEnums.DateComparisonResult['FirstIsBeforeSecond']
		elif Date1['month'] > Date2['month']:
			return IbViewEnums.DateComparisonResult['FirstIsAfterSecond']
		else:
			if Date1['day'] < Date2['day']:
				return IbViewEnums.DateComparisonResult['FirstIsBeforeSecond']
			elif Date1['day'] > Date2['day']:
				return IbViewEnums.DateComparisonResult['FirstIsAfterSecond']
			else:
				return IbViewEnums.DateComparisonResult['DatesAreEqual']

def LogError(message):
	ErrorTimestamp = datetime.datetime.now()
	ErrorTimeString = '{0:%A} {0:%B} {0:%d}, {0:%Y} @ {0:%I:%M%p} '.format(ErrorTimestamp)
	FormattedErrorString = ErrorTimeString + message
	IbViewGui.GuiShowDevelopmentMessage(FormattedErrorString)
	print(FormattedErrorString)
