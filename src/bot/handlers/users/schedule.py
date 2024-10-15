from aiogram import F, Router
from aiogram.types import Message

import utils.constants as const
from bot.keyboards.reply.main_kb import get_main_kb
from database.cache import Cache
from database.models.groups import GroupModel
from database.models.users import UserModel
from database.redis.base import create_redis
from database.repository import Repository
from services.parser_service.week import Week

router = Router(name=__name__)
redis = create_redis()


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message,
                          user: UserModel, repository: Repository):
    group: GroupModel = user.group

    result_schedule = Cache(redis).schedule.get(Week().weekday,
                                                group.name)
    if result_schedule is None:
        result_schedule_data = await repository.result_schedule.get(Week().weekday,
                                                                    user.group_id)
        if result_schedule_data is not None:
            result_schedule = result_schedule_data.data_lessons

    if result_schedule is None:
        await message.answer(const.NO_SCHEDULE_TEXT,
                             reply_markup=get_main_kb(message.from_user.id))
        return

    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message,
                                   user: UserModel, repository: Repository):
    previous_weekday = get_previous_weekday(Week().weekday)

    result_schedule = await repository.result_schedule.get(previous_weekday,
                                                           user.group_id)
    if result_schedule is None:
        await message.answer(const.NO_SCHEDULE_TEXT,
                             reply_markup=get_main_kb(message.from_user.id))
        return

    result_schedule = result_schedule.data_lessons
    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message,
                               user: UserModel, repository: Repository):
    next_weekday = get_next_weekday(Week().weekday)

    result_schedule = await repository.result_schedule.get(next_weekday,
                                                           user.group_id)
    if result_schedule is None:
        await message.answer(const.NO_SCHEDULE_TEXT,
                             reply_markup=get_main_kb(message.from_user.id))
        return

    result_schedule = result_schedule.data_lessons
    await message.answer(result_schedule,
                         reply_markup=get_main_kb(message.from_user.id))


def get_previous_weekday(weekday: int) -> int:
    return weekday - 1 if weekday != 0 else 6


def get_next_weekday(weekday: int) -> int:
    return weekday + 1 if weekday != 6 else 0
