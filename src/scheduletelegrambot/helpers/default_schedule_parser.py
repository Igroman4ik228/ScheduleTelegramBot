import ast
from typing import Any

from scheduletelegrambot.helpers.lesson import Lesson


def generate_default_schedule(data_lessons: str):
    default_lessons = ast.literal_eval(data_lessons)
    for default_lesson in default_lessons:
        yield Lesson.from_dict(default_lesson)


def get_default_lessons(data_lessons: str) -> list[Lesson]:
    default_lessons = ast.literal_eval(data_lessons)

    return [Lesson.from_dict(default_lesson) for default_lesson in default_lessons]


def default_schedule_parse(
    data: dict[str, Any],
) -> dict[int, dict[int, list[Any]]]:
    schedule_data = {}
    for shift_str, weekdays in data.items():
        shift = int(shift_str)
        schedule_data[shift] = {}

        for weekday_str, lessons in weekdays.items():
            weekday = int(weekday_str)
            schedule_data[shift][weekday] = list(lessons)

    return schedule_data
