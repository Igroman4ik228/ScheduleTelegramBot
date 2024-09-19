import constants
from ParserService.element_finder import ElementFinder


class Week():
    def __init__(self, weekday: int, shift: int):
        self.weekday = weekday
        self.shift = shift

    @staticmethod
    def get_weekday(finder: ElementFinder) -> int:
        day_of_week_name = finder.get_text_from_div(index=2).lower()
        day_of_week = get_key(constants.DAY_NAMES, day_of_week_name)

        return day_of_week

    @staticmethod
    def get_shift(finder: ElementFinder) -> int:
        week_schedule_name = finder.get_text_from_div(index=3, word_index=0)
        week_schedule_name = week_schedule_name.strip("()").lower()

        week_schedule = constants.WEEK_SCHEDULE_MAPPING.get(week_schedule_name)

        if week_schedule is None:
            raise ValueError(
                f"Не удалось определить числитель/знаменатель. Значение: {week_schedule_name}")

        return week_schedule


def get_key(input_dict: dict, target_value):
    for key, value in input_dict.items():
        if value == target_value:
            return key
    raise ValueError(f"{target_value} не найден в {input_dict}")
