import utils.constants as const
from helpers.algorithm import get_key
from helpers.singleton import SingletonMeta


class Week(metaclass=SingletonMeta):
    def initialize(self, weekday: int, shift: int):
        self.weekday = weekday
        self.shift = shift

    def get_weekday_name(self) -> str:
        return const.DAY_NAMES.get(self.weekday, "Неизвестный день")

    def get_shift_name(self) -> str:
        return get_key(const.WEEK_SCHEDULE_MAPPING, self.shift) or "Неизвестная смена"
