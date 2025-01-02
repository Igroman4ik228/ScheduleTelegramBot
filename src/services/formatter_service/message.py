from database.models import DefaultScheduleModel
from helpers.default_schedule_parser import generate_default_schedule
from services.formatter_service.schedule import format_header, format_lesson
from utils.constants import DAY_NAMES


def format_default_schedules(default_schedules: list[DefaultScheduleModel], shift: int) -> str:
    formatted_default_schedules = ""
    for weekday, schedule in enumerate(default_schedules):
        if weekday > len(DAY_NAMES) - 1:
            raise IndexError("Неверный индекс дня недели")

        formatted_default_schedules += format_header(
            weekday, shift, is_default_schedule=True
        )
        formatted_default_schedules += format_default_schedule(schedule)

        if weekday != len(DAY_NAMES) - 1:
            formatted_default_schedules += "\n"

    return formatted_default_schedules


def format_default_schedule(default_schedule: DefaultScheduleModel) -> str:
    formatted_default_schedule = ""
    for default_lesson in generate_default_schedule(default_schedule.data_lessons):
        formatted_default_schedule += format_lesson(default_lesson)

    return formatted_default_schedule
