import ast

from helpers.lesson import Lesson


def generate_default_schedule(data_lessons: str):
    default_lessons = ast.literal_eval(data_lessons)
    for default_lesson in default_lessons:
        yield Lesson.from_dict(default_lesson)


def build_default_schedule(data_lessons: str):
    default_schedule = []
    default_lessons = ast.literal_eval(data_lessons)
    for default_lesson in default_lessons:
        default_schedule.append(Lesson.from_dict(default_lesson))

    return default_schedule
