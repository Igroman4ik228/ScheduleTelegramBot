from aiogram import F, Router
from aiogram.types import Message

import utils.constants as const
from bot.keyboards.reply.main_kb import get_main_kb
from database.db import sessionmaker
from database.models.groups import GroupModel
from database.redis_cache import ScheduleCache, create_redis
from database.repositories.result_schedule import ResultScheduleRepository
from database.repositories.users import UserRepository
from parser_service.week import Week

router = Router(name=__name__)
redis = create_redis()


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message):
    async with sessionmaker() as session:
        user = await UserRepository(session).get_with_group(message.from_user.id)
        group: GroupModel = user.group
        result_schedule = ScheduleCache(redis).get_schedule(Week.weekday,
                                                            group.name)
        if result_schedule is None:
            result_schedule_data = await ResultScheduleRepository(session).get(Week.weekday,
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
async def handle_previous_schedule(message: Message):
    previous_weekday = get_previous_weekday(Week.weekday)

    async with sessionmaker() as session:
        user = await UserRepository(session).get(message.from_user.id)
        result_schedule = await ResultScheduleRepository(session).get(previous_weekday,
                                                                      user.group_id)

    if result_schedule is None:
        await message.answer(const.NO_SCHEDULE_TEXT,
                             reply_markup=get_main_kb(message.from_user.id))
        return

    await message.answer(result_schedule.data_lessons,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message):
    next_weekday = get_next_weekday(Week.weekday)

    async with sessionmaker() as session:
        user = await UserRepository(session).get(message.from_user.id)
        result_schedule = await ResultScheduleRepository(session).get(next_weekday,
                                                                      user.group_id)

    if result_schedule is None:
        await message.answer(const.NO_SCHEDULE_TEXT,
                             reply_markup=get_main_kb(message.from_user.id))
        return

    await message.answer(result_schedule.data_lessons,
                         reply_markup=get_main_kb(message.from_user.id))


def get_previous_weekday(weekday: int) -> int:
    return weekday - 1 if weekday != 0 else 6


def get_next_weekday(weekday: int) -> int:
    return weekday + 1 if weekday != 6 else 0
