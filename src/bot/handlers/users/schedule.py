from aiogram import F, Router
from aiogram.types import Message

import utils.constants as const
from bot.keyboards.reply.main_kb import get_main_kb
from database.models.default_schedule import DefaultScheduleModel
from database.models.result_schedule import ResultScheduleModel
from database.models.users import UserModel
from database.repository import Repository
from helpers.generator import build_default_schedule
from services.formatter_service.schedule import (add_time_to_schedule,
                                                 format_schedule)
from services.parser_service.week import Week

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message,
                          user: UserModel, repository: Repository):
    result_schedule_data = await repository.result_schedule.get(Week().weekday,
                                                                user.group_id)
    result_schedule = process_schedule(user, result_schedule_data)

    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message,
                                   user: UserModel, repository: Repository):
    previous_weekday = get_previous_weekday(Week().weekday)
    previous_shift = get_previous_shift(Week().shift, Week().weekday)

    result_schedule_data = await repository.result_schedule.get(previous_weekday,
                                                                user.group_id)
    result_schedule = ""
    if not validate_schedule_data(result_schedule_data):
        default_schedule_data = await repository.default_schedule.get(previous_weekday,
                                                                      previous_shift,
                                                                      user.group_id)
        if validate_schedule_data(default_schedule_data):
            default_schedule = build_default_schedule(
                default_schedule_data.data_lessons
            )
            result_schedule = format_schedule(default_schedule)

        else:
            result_schedule = const.NO_SCHEDULE_TEXT

    else:
        result_schedule = result_schedule_data.data_lessons

    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message,
                               user: UserModel, repository: Repository):
    next_weekday = get_next_weekday(Week().weekday)
    next_shift = get_next_shift(Week().shift, Week().weekday)

    default_schedule_data = await repository.default_schedule.get(next_weekday,
                                                                  next_shift,
                                                                  user.group_id)
    result_schedule = ""
    if validate_schedule_data(default_schedule_data):
        default_schedule = build_default_schedule(
            default_schedule_data.data_lessons
        )
        result_schedule = format_schedule(default_schedule)
    else:
        result_schedule = const.NO_SCHEDULE_TEXT

    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


def process_schedule(user: UserModel,
                     result_schedule_data: ResultScheduleModel | None) -> str:
    if not validate_schedule_data(result_schedule_data):
        return const.NO_SCHEDULE_TEXT

    result_schedule = result_schedule_data.data_lessons
    if user.is_time_shown:
        result_schedule = add_time_to_schedule(result_schedule)

    return result_schedule


def validate_schedule_data(
    schedule_data: ResultScheduleModel | DefaultScheduleModel | None
) -> bool:
    if schedule_data is None or not schedule_data.data_lessons:
        return False

    return True


def get_previous_weekday(weekday: int) -> int:
    return weekday - 1 if weekday != 0 else 6


def get_next_weekday(weekday: int) -> int:
    return weekday + 1 if weekday != 6 else 0


def get_previous_shift(shift: int, weekday: int) -> int:
    if weekday == 0:
        return 2 if shift == 1 else 1
    return shift


def get_next_shift(shift: int, weekday: int) -> int:
    if weekday == 5:
        return 2 if shift == 1 else 1
    return shift
