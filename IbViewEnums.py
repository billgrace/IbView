import SharedVars

from enum import Enum

class RequestedMonitorStatus(Enum):
	NotSpecifed = 0
	Pending = 1
	Active = 2
	RejectedByIB = 3

class ReadRequestResultReturnCode(Enum):
	NotSpecifed = 0
	Success = 1
	IdNotOnActiveList = 2

class DateComparisonResult(Enum):
	NotSpecified = 0
	FirstIsBeforeSecond = 1
	DatesAreEqual = 2
	FirstIsAfterSecond = 3
