from dataclasses import dataclass

from helpers.algorithm import get_key
from utils.constants import DAY_NAMES, WEEK_SCHEDULE_MAPPING


@dataclass
class Week:
    weekday: int
    shift: int

    def get_previous_weekday(self) -> int:
        return self.weekday - 1 if self.weekday != 0 else 5

    def get_next_weekday(self) -> int:
        return self.weekday + 1 if self.weekday != 5 else 0

    def get_previous_shift(self) -> int:
        if self.weekday == 0:
            return 2 if self.shift == 1 else 1
        return self.shift

    def get_next_shift(self) -> int:
        if self.weekday == 5:
            return 2 if self.shift == 1 else 1
        return self.shift

    @staticmethod
    def get_weekday_name_by_weekday(weekday: int) -> str:
        return DAY_NAMES.get(weekday, "Неизвестный день")

    @staticmethod
    def get_shift_name_by_shift(shift: int) -> str:
        return get_key(WEEK_SCHEDULE_MAPPING, shift) or "Неизвестная смена"
