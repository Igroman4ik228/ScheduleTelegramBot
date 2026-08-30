from enum import Enum


class Weekday(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


class WeekType(Enum):
    NUMERATOR = "numerator"
    DENOMINATOR = "denominator"


class StudyShift(Enum):
    FIRST = "1"
    SECOND = "2"
