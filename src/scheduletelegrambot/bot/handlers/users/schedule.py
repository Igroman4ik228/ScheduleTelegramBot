from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from scheduletelegrambot.app.factory_pack.parser_factory import (
    ParserFactory,
)
from scheduletelegrambot.bot.keyboards.users.reply.main_kb import get_main_kb
from scheduletelegrambot.components.formatters.schedule import add_time_to_schedule
from scheduletelegrambot.schemas.user import UserWithAllSchema
from scheduletelegrambot.services.schedule import (
    ScheduleService,
)
from scheduletelegrambot.settings import Settings

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(
    message: Message,
    parser_factory: FromDishka[ParserFactory],
    user: UserWithAllSchema,
    schedules: FromDishka[ScheduleService],
    settings: FromDishka[Settings],
):
    group = user.group
    if group is None or user.group_id is None:
        await message.answer("Сначала выберите группу")
        return

    week = parser_factory.get_week(group.global_shift)

    schedule = await schedules.get(user.group_id, week.weekday, week.shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(
        schedule,
        reply_markup=get_main_kb(user.telegram_id, settings.bot.admin_ids),
    )


@router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(
    message: Message,
    parser_factory: FromDishka[ParserFactory],
    user: UserWithAllSchema,
    schedules: FromDishka[ScheduleService],
    settings: FromDishka[Settings],
):
    group = user.group
    if group is None or user.group_id is None:
        await message.answer("Сначала выберите группу")
        return
    week = parser_factory.get_week(group.global_shift)

    previous_weekday = week.get_previous_weekday()
    previous_shift = week.get_previous_shift()

    schedule = await schedules.get(user.group_id, previous_weekday, previous_shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(
        schedule,
        reply_markup=get_main_kb(user.telegram_id, settings.bot.admin_ids),
    )


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(
    message: Message,
    parser_factory: FromDishka[ParserFactory],
    user: UserWithAllSchema,
    schedules: FromDishka[ScheduleService],
    settings: FromDishka[Settings],
):
    group = user.group
    if group is None or user.group_id is None:
        await message.answer("Сначала выберите группу")
        return
    week = parser_factory.get_week(group.global_shift)

    next_weekday = week.get_next_weekday()
    next_shift = week.get_next_shift()

    schedule = await schedules.get_default(user.group_id, next_weekday, next_shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(
        schedule,
        reply_markup=get_main_kb(user.telegram_id, settings.bot.admin_ids),
    )
