import SharedVars
import IbViewEnums

class DateClass(dict):
	def __init__(self):
	# def __init__(self, *args, **kwargs):
		self['year'] = 2016
		self['month'] = 1
		self['day'] = 1

class OptionCompStructureClass(dict):
	def __init__(self):
	# def __init__(self, *args, **kwargs):
		self['Price'] = 0.0
		self['Size'] = 0
		self['ImpliedVolatility'] = 0.0
		self['Delta'] = 0.0
		self['Theta'] = 0.0
		self['Gamma'] = 0.0
		self['Vega'] = 0.0

class MonitorDataClass(dict):
	def __init__(self):
	# def __init__(self, *args, **kwargs):
		ed = DateClass()
		aoc = OptionCompStructureClass()
		boc = OptionCompStructureClass()
		loc = OptionCompStructureClass()
		moc = OptionCompStructureClass()
		self['MonitorStatus'] = IbViewEnums.RequestedMonitorStatus['NotSpecified'].name
		self['RequestSuccessCode'] = IbViewEnums.ReadRequestResultReturnCode['NotSpecified'].name
		self['SequenceNumber'] = 0
		self['MonitorStartMilliseconds'] = 0
		self['MonitorLastUpdateMilliseconds'] = 0
		self['MonitorUpdateCount'] = 0
		self['Symbol'] = ''
		self['ExpirationDate'] = ed
		self['ContractRight'] = ''
		self['StrikePrice'] = 0.0
		self['SubscriptionId'] = 0
		self['Ask'] = aoc
		self['Bid'] = boc
		self['Last'] = loc
		self['Model'] = moc
		self['Volume'] = 0
		self['TimeStamp'] = ''
		self['Open'] = 0.0
		self['High'] = 0.0
		self['Low'] = 0.0
		self['Close'] = 0.0

class LoggedDataRecordTimestampClass(dict):
	def __init__(self):
		self['Hour'] = 1
		self['Minute'] = 1
		self['Second'] = 1
		self['Millisecond'] = 1

class LoggedDataRecordClass(dict):
	def __init__(self):
		self['Timestamp'] = LoggedDataRecordTimestampClass()
		self['MonitorData'] = MonitorDataClass()
		self['RecordAppearsValid'] = False

class ImportedDataFileClass(dict):
	def __init__(self):
		self['FileName'] = ''
		self['FileRecordList'] = []
		self['ValidRecordIndexList'] = []

class DataFileDescriptor(dict):
	def __init__(self):
		self['FileName'] = 'PlaceHolder'
		self['LogHour'] = 6.0
		self['LogDay'] = 1
		self['LogMonth'] = 1
		self['LogYear'] = 2018
		self['FileType'] = 'Underlying'
		self['StrikePrice'] = 2000
		self['ExpirationYear'] = 2018
		self['ExpirationMonth'] = 1
		self['ExpirationDay'] = 1
		self['ContractRight'] = 'CALL'
		self['QueuedHour'] = 6.0
		self['QueuedMinute'] = 1.0
		self['QueuedSecond'] = 1.0

class DayDataDescriptors(dict):
	def __init__(self):
		self['DataYear'] = 2018
		self['DataMonth'] = 1
		self['DataDay'] = 1
		self['SixOclockFileDescriptorIndex']
		self['SevenOclockFileDescriptorIndex']
		self['EightOclockFileDescriptorIndex']
		self['NineOclockFileDescriptorIndex']
		self['TenOclockFileDescriptorIndex']
		self['ElevenOclockFileDescriptorIndex']
		self['TwelveOclockFileDescriptorIndex']
		self['ThirteenOclockFileDescriptorIndex']

