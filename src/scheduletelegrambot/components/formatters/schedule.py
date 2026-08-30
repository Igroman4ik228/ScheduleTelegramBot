import re

from aiogram import html

from scheduletelegrambot.enums import Weekday, WeekType
from scheduletelegrambot.helpers.lesson import Lesson, TeachingAssignment
from scheduletelegrambot.helpers.week import Week
from scheduletelegrambot.utils.constants import DAY_NAME_CASES

REPLACEMENT_TEXT = "(❗️ замена)"


def format_schedule(lessons: list[Lesson], weekday: Weekday, week_type: WeekType) -> str:
    return format_header(weekday, week_type) + format_lessons(lessons)


def format_header(
    weekday: Weekday, week_type: WeekType, *, is_default_schedule: bool = False
) -> str:
    weekday_name = Week.get_weekday_name(weekday)
    weekday_name = html.bold(DAY_NAME_CASES.get(weekday_name, weekday_name))
    if is_default_schedule:
        return f"Расписание на {weekday_name}\n"
    week_type_name = Week.get_week_type_name(week_type)
    return html.blockquote(f"Расписание на {weekday_name} ({week_type_name})") + "\n"


def format_lessons(lessons: list[Lesson]) -> str:
    sorted_lessons = sorted(lessons, key=lambda lesson: lesson.number)
    return "".join(format_lesson(lesson) for lesson in sorted_lessons)


def format_lesson(lesson: Lesson) -> str:
    formatted_lesson = html.link(f"{lesson.number}. ", "https://ygk.edu.yar.ru")
    if lesson.time is not None:
        formatted_lesson += html.italic(lesson.time.strftime("%H:%M"))
    formatted_lesson += lesson.subject
    assignments = _merge_assignments(lesson.teaching_assignments)
    if assignments:
        if assignments[0].teacher:
            formatted_lesson += "\n↳ " + "; ".join(_format_assignment(item) for item in assignments)
        else:
            formatted_lesson += f" [{html.bold(', '.join(assignments[0].classrooms))}]"
    if lesson.is_replacement:
        formatted_lesson += " " + REPLACEMENT_TEXT
    return formatted_lesson + "\n"


def _merge_assignments(assignments: list[TeachingAssignment]) -> list[TeachingAssignment]:
    merged: dict[str, list[str]] = {}
    for assignment in assignments:
        classrooms = merged.setdefault(assignment.teacher, [])
        for classroom in assignment.classrooms:
            if classroom not in classrooms:
                classrooms.append(classroom)
    return [
        TeachingAssignment(teacher, tuple(classrooms)) for teacher, classrooms in merged.items()
    ]


def _format_assignment(assignment: TeachingAssignment) -> str:
    return f"{assignment.teacher} — {html.bold(', '.join(assignment.classrooms))}"


def add_time_to_schedule(schedule: str, skip_lines: int = 1) -> str:
    result_lines: list[str] = []
    lines = schedule.split("\n")
    for line in lines[skip_lines:]:
        lesson_number = get_lesson_number(line)
        if lesson_number is None:
            result_lines.append(line)
            continue
        try:
            full_time = Lesson.get_full_time(lesson_number)
        except ValueError:
            result_lines.append(line)
            continue
        result_lines.append(f"{line} <i>{full_time}</i>")
    return f"{lines[0]}\n{'\n'.join(result_lines)}"


def get_lesson_number(lesson: str) -> int | None:
    match = re.match(r'<a href="https://ygk\.edu\.yar\.ru">(\d+)\. </a>', lesson)
    return int(match.group(1)) if match else None
