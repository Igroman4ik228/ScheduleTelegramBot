from aiogram import html

from database.db import sessionmaker
from database.models.default_schedule import DefaultScheduleModel
from database.models.departments import DepartmentModel
from database.models.groups import GroupModel
from database.models.subscribe import SubscribeModel
from database.models.users import UserModel
from database.repository import Repository
from helpers.default_schedule_parser import generate_default_schedule
from services.formatter_service.schedule import format_header, format_lesson
from utils.constants import DAY_NAMES


class ProfileFormatter:
    def __init__(self, user: UserModel, group: GroupModel,
                 department: DepartmentModel, subscribe: SubscribeModel | None):
        self.user = user
        self.group: GroupModel = group
        self.department: DepartmentModel = department
        self.subscribe: SubscribeModel | None = subscribe

    def format_info(self, title: str) -> str:
        if self.subscribe:
            subscribe_name = f"{self.subscribe.name} "
            end_time = self.user.subscribe_end_time.strftime('%d.%m.%Y')

            subscribe_name += f"(действует до {end_time})"
        else:
            subscribe_name = "Подписка отсутствует"

        return (
            f"{html.blockquote(title)}\n"
            f"Отделение: {self.department.name}\n"
            f"Группа: {self.group.name}\n"
            f"{subscribe_name}\n"
        )


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
