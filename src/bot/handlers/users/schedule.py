from aiogram import F, Router
from aiogram.types import Message

import utils.constants as const
from bot.keyboards.users.reply.main_kb import get_main_kb
from database.models.default_schedule import DefaultScheduleModel
from database.models.result_schedule import ResultScheduleModel
from database.models.users import UserModel
from database.repository import Repository
from helpers.default_schedule_parser import generate_default_schedule
from helpers.lesson import Lesson
from helpers.week import Week
from services.formatter_service.schedule import (add_time_to_schedule,
                                                 format_schedule)

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message,
                          user: UserModel, repository: Repository):
    schedule = await get_schedule(user.group_id, repository,
                                  Week().weekday, Week().shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message,
                                   user: UserModel, repository: Repository):
    previous_weekday = Week().get_previous_weekday()
    previous_shift = Week().get_previous_shift()

    schedule = await get_schedule(user.group_id, repository,
                                  previous_weekday, previous_shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message,
                               user: UserModel, repository: Repository):
    next_weekday = Week().get_next_weekday()
    next_shift = Week().get_next_shift()

    schedule = await get_default_schedule(user.group_id, repository,
                                          next_weekday, next_shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(schedule,
                         reply_markup=get_main_kb(message.from_user.id))


async def get_schedule(
    group_id: int,
    repository: Repository,
    weekday: int,
    shift: int
) -> str:
    result_schedule_data = await repository.result_schedule.get(weekday,
                                                                group_id)
    if validate_schedule(result_schedule_data):
        result_schedule = result_schedule_data.data_lessons + "\n"
        return result_schedule + f"{const.MARKERS[0]} {const.WITH_VERIFICATION_TEXT}"

    default_schedule = await get_default_schedule(
        group_id, repository, weekday, shift
    )
    return default_schedule


async def get_default_schedule(
    group_id: int,
    repository: Repository,
    weekday: int,
    shift: int
) -> str:
    default_schedule_data = await repository.default_schedule.get(
        weekday, shift, group_id
    )
    if not validate_schedule(default_schedule_data):
        return const.NO_SCHEDULE_TEXT

    default_schedule = build_default_schedule(
        default_schedule_data.data_lessons
    )
    default_schedule = format_schedule(
        default_schedule, weekday, shift
    ) + "\n"

    return default_schedule + f"{const.MARKERS[1]} {const.WITHOUT_VERIFICATION_TEXT}"


def build_default_schedule(
    default_schedule: str
) -> list[Lesson]:
    lessons = []
    for lesson in generate_default_schedule(default_schedule):
        lessons.append(lesson)

    return lessons


def validate_schedule(schedule: ResultScheduleModel | DefaultScheduleModel | None) -> bool:
    if schedule is None or schedule.data_lessons is None:
        return False

    return True
