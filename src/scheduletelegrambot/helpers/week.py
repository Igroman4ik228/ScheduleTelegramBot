from dataclasses import dataclass

from scheduletelegrambot.enums import Weekday, WeekType
from scheduletelegrambot.utils.constants import DAY_NAMES, WEEK_TYPE_NAMES


@dataclass(frozen=True)
class Week:
    weekday: Weekday
    week_type: WeekType

    def get_previous_weekday(self) -> Weekday:
        weekdays = list(Weekday)
        return weekdays[(weekdays.index(self.weekday) - 1) % len(weekdays)]

    def get_next_weekday(self) -> Weekday:
        weekdays = list(Weekday)
        return weekdays[(weekdays.index(self.weekday) + 1) % len(weekdays)]

    def get_previous_week_type(self) -> WeekType:
        return WeekType.DENOMINATOR if self.weekday is Weekday.MONDAY else self.week_type

    def get_next_week_type(self) -> WeekType:
        return WeekType.NUMERATOR if self.weekday is Weekday.SATURDAY else self.week_type

    @staticmethod
    def get_weekday_name(weekday: Weekday) -> str:
        return DAY_NAMES[weekday]

    @staticmethod
    def get_week_type_name(week_type: WeekType) -> str:
        return WEEK_TYPE_NAMES[week_type]
