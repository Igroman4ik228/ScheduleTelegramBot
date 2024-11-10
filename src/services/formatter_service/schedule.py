import re

from aiogram import html

from helpers.lesson import Lesson
from services.parser_service.week import Week
from utils.constants import DAY_NAME_CASES


def format_schedule(lessons: list[Lesson]) -> str:
    return format_header() + format_lessons(lessons)


def format_header(is_default_schedule: bool = False) -> str:
    weekday_name = Week().get_weekday_name()
    weekday_name = DAY_NAME_CASES.get(weekday_name, weekday_name)
    weekday_name = html.bold(weekday_name)

    if not is_default_schedule:
        shift = Week().get_shift_name()
        header = html.blockquote(f"Расписание на {weekday_name} ({shift})")
    else:
        header = f"Расписание на {weekday_name}\n"
    return header


def format_lessons(lessons: list[Lesson]) -> str:
    lessons = sort_lessons(lessons)
    formatted_lessons = ""
    for lesson in lessons:
        formatted_lessons += format_lesson(lesson)

    return formatted_lessons


def sort_lessons(lessons: list[Lesson]) -> list[Lesson]:
    return sorted(lessons, key=lambda lesson: lesson.number)


def format_lesson(lesson: Lesson) -> str:
    formatted_lesson = html.link(
        f"{lesson.number}. ",
        "https://ygk.edu.yar.ru"
    )

    if lesson.time is not None:
        formatted_lesson += html.italic(lesson.time)

    formatted_lesson += f"{lesson.subject}"

    if lesson.classroom != '':
        classroom = html.bold(lesson.classroom)
        formatted_lesson += f" [{classroom}]"

    if lesson.is_replacement:
        formatted_lesson += " (❗️ замена)"
    formatted_lesson += "\n"

    return formatted_lesson


def add_time_to_schedule(schedule: str, skip_lines: int = 1) -> str:
    result_lessons: list[str] = []

    lines = schedule.split('\n')
    lessons = lines[skip_lines:]
    for lesson in lessons:
        if not lesson:
            continue

        lesson_number = get_lesson_number(lesson)
        if lesson_number is None:
            continue

        full_time = Lesson.get_full_time(lesson_number)
        result_lesson = f"{lesson} <i>{full_time}</i>"

        result_lessons.append(result_lesson)

    header_schedule = lines[0]
    result_lessons_str = '\n'.join(result_lessons)

    return f"{header_schedule}\n{result_lessons_str}"


def get_lesson_number(lesson: str) -> int | None:
    match = re.search(r"\d+", lesson)
    return int(match.group()) if match else None
