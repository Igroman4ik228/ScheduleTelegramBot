from aiogram import F, Router
from aiogram.types import Message

import utils.constants as const
from bot.keyboards.reply.main_kb import get_main_kb
from database.models.result_schedule import ResultScheduleModel
from database.models.users import UserModel
from database.repository import Repository
from services.formatter_service.schedule import ScheduleFormatter
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
    result_schedule_data = await repository.result_schedule.get(previous_weekday,
                                                                user.group_id)
    result_schedule = process_schedule(user, result_schedule_data)

    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message,
                               user: UserModel, repository: Repository):
    next_weekday = get_next_weekday(Week().weekday)
    result_schedule_data = await repository.result_schedule.get(next_weekday,
                                                                user.group_id)
    result_schedule = process_schedule(user, result_schedule_data)

    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


def process_schedule(user: UserModel,
                     result_schedule_data: ResultScheduleModel | None) -> str:
    if result_schedule_data is None or not result_schedule_data.data_lessons:
        return const.NO_SCHEDULE_TEXT

    result_schedule = result_schedule_data.data_lessons
    if user.is_time_shown:
        result_schedule = ScheduleFormatter.add_time_to_schedule(
            result_schedule
        )

    return result_schedule


def get_previous_weekday(weekday: int) -> int:
    return weekday - 1 if weekday != 0 else 6


def get_next_weekday(weekday: int) -> int:
    return weekday + 1 if weekday != 6 else 0
