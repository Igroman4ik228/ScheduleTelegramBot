import utils.constants as const
from services.parser_service.element_finder import ElementFinder
from utils.different import get_key


class Week:
    @classmethod
    def initialize(cls, finder: ElementFinder):
        cls.weekday = cls._get_weekday(finder)
        cls.shift = cls._get_shift(finder)

    @classmethod
    def _get_weekday(cls, finder: ElementFinder) -> int:
        weekday_name = finder.get_text_from_div(index=2)
        weekday_name = weekday_name.strip().lower()

        weekday = get_key(const.DAY_NAMES, weekday_name)
        if weekday is None:
            raise ValueError(
                f"Не удалось определить день недели: {weekday_name}"
            )

        return weekday

    @classmethod
    def _get_shift(cls, finder: ElementFinder) -> int:
        shift_name = finder.get_text_from_div(index=3, word_index=0)
        shift_name = shift_name.strip("()").lower()

        shift = const.WEEK_SCHEDULE_MAPPING.get(shift_name)
        if shift is None:
            raise ValueError(
                f"Не удалось определить числитель/знаменатель. Значение: {shift_name}")

        return shift

    @classmethod
    def get_weekday_name(cls) -> str:
        return const.DAY_NAMES.get(cls.weekday, "Неизвестный день")

    @classmethod
    def get_shift_name(cls) -> str:
        return get_key(const.WEEK_SCHEDULE_MAPPING, cls.shift) or "Неизвестный смена"
