from aiogram import F, Router
from aiogram.types import Message

from database.db import sessionmaker
from database.repositories.result_schedule import ResultScheduleRepository
from database.repositories.users import UserRepository
from parser_service.parser import ParserService
from utils import constants

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message):
    async with sessionmaker() as session:
        user = await UserRepository(session).get(message.from_user.id)
        if user.group_id is None:
            await message.answer("Выберите группу, пожалуйста")
            return

        result_schedule = await ResultScheduleRepository(session).get(ParserService.weekday,
                                                                      user.group_id)

    if result_schedule is None:
        await message.answer(constants.NO_SCHEDULE_TEXT)
        return

    await message.answer(result_schedule.data_lessons)


@router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message):
    previous_weekday = get_previous_weekday(ParserService.weekday)

    async with sessionmaker() as session:
        user = await UserRepository(session).get(message.from_user.id)
        if user.group_id is None:
            await message.answer("Выберите группу, пожалуйста")
            return

        result_schedule = await ResultScheduleRepository(session).get(previous_weekday,
                                                                      user.group_id)

    if result_schedule is None:
        await message.answer(constants.NO_SCHEDULE_TEXT)
        return

    await message.answer(result_schedule.data_lessons)


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message):
    next_weekday = get_next_weekday(ParserService.weekday)

    async with sessionmaker() as session:
        user = await UserRepository(session).get(message.from_user.id)
        if user.group_id is None:
            await message.answer("Выберите группу, пожалуйста")
            return

        result_schedule = await ResultScheduleRepository(session).get(next_weekday,
                                                                      user.group_id)

    if result_schedule is None:
        await message.answer(constants.NO_SCHEDULE_TEXT)
        return

    await message.answer(result_schedule.data_lessons)


def get_previous_weekday(weekday: int) -> int:
    return weekday - 1 if weekday != 0 else 6


def get_next_weekday(weekday: int) -> int:
    return weekday + 1 if weekday != 6 else 0
