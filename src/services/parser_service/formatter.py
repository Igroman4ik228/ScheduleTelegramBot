import re
from logging import getLogger

from services.parser_service.lesson import Lesson
from services.parser_service.week import Week
from utils.constants import DAY_NAME_CASES


class ScheduleFormatter:
    def __init__(self, lessons: list[Lesson]):
        self.logger = getLogger(__name__)
        self.lessons = sorted(
            lessons,
            key=lambda lesson: lesson.number
        )

    def format_schedule(self) -> str:
        return self.format_header() + self.format_lessons()

    def format_header(self) -> str:
        weekday_name = Week().get_weekday_name()
        weekday_name = DAY_NAME_CASES.get(weekday_name, weekday_name)
        weekday_name = add_html_tag(weekday_name, "b")

        shift = Week().get_shift_name()

        header = add_html_tag(
            f"Расписание на {weekday_name} ({shift})",
            "blockquote"
        )
        return header + "\n"

    def format_lessons(self) -> str:
        formatted_lessons = ""
        for lesson in self.lessons:
            formatted_lessons += self.format_lesson(lesson)

        return formatted_lessons

    def format_lesson(self, lesson: Lesson) -> str:
        formatted_lesson = add_html_tag(
            f"{lesson.number}. ",
            "a",
            {"href": "https://ygk.edu.yar.ru"}
        )

        if lesson.time is not None:
            formatted_lesson += add_html_tag(
                lesson.time,
                "i"
            )

        formatted_lesson += f"{lesson.subject}"

        if lesson.classroom != '':
            classroom = add_html_tag(
                lesson.classroom,
                "b"
            )
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


def add_html_tag(text: str, tag: str, attributes: dict = None) -> str:
    if attributes:
        attributes_tag = ' '.join(
            [f'{k}="{v}"' for k, v in attributes.items()]
        )
        return f"<{tag} {attributes_tag}>{text}</{tag}>"

    return f"<{tag}>{text}</{tag}>"


def get_lesson_number(lesson: str) -> int | None:
    match = re.search(r"\d+", lesson)
    return int(match.group()) if match else None
