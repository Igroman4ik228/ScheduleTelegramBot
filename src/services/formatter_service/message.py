from database.models.default_schedule import DefaultScheduleModel
from database.models.departments import DepartmentModel
from database.models.groups import GroupModel
from database.models.subscribe import SubscribeModel
from database.models.users import UserModel
from helpers.generator import generate_default_schedule
from services.formatter_service.schedule import format_header, format_lesson


def format_info(user: UserModel, header: str) -> str:
    group: GroupModel = user.group
    department: DepartmentModel = group.department

    if user.subscribe_id or user.subscribe_end_time:
        subscribe: SubscribeModel = user.subscribe
        subscribe_name = f"{subscribe.name} "
        end_time = user.subscribe_end_time.strftime('%d.%m.%Y')
        subscribe_name += f"(действует до {end_time})"
    else:
        subscribe_name = "Подписка отсутствует"

    return (
        f"<blockquote>{header}</blockquote>\n"
        f"Отделение: {department.name}\n"
        f"Группа: {group.name}\n"
        f"{subscribe_name}\n"
    )


def format_default_schedules(default_schedules: list[DefaultScheduleModel]) -> str:
    formatted_default_schedules = ""
    for schedule in default_schedules:
        formatted_default_schedules += format_header(is_default_schedule=True)
        formatted_default_schedules += format_default_schedule(schedule)
        formatted_default_schedules += "\n"
    return formatted_default_schedules


def format_default_schedule(default_schedule: DefaultScheduleModel) -> str:
    formatted_default_schedule = ""
    for default_lesson in generate_default_schedule(default_schedule.data_lessons):
        formatted_default_schedule += format_lesson(default_lesson)

    return formatted_default_schedule
