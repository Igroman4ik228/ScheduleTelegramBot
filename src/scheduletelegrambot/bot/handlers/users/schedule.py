from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message  # noqa: TC002 - evaluated by Dishka.
from dishka.integrations.aiogram import FromDishka, inject

from scheduletelegrambot.app.factory_pack.parser_factory import (  # noqa: TC001 - evaluated by Dishka.
    ParserFactory,
)
from scheduletelegrambot.bot.keyboards.users.reply.main_kb import get_main_kb
from scheduletelegrambot.bot.views.schedule import ScheduleView
from scheduletelegrambot.components.formatters.schedule import (
    add_time_to_schedule,
    format_schedule,
)
from scheduletelegrambot.database.models import UserModel  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.helpers.default_schedule_parser import (
    generate_default_schedule,
)
from scheduletelegrambot.helpers.lesson import Lesson  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.services.default_schedule import (  # noqa: TC001 - evaluated by Dishka.
    DefaultScheduleService,
)
from scheduletelegrambot.services.result_schedule import (  # noqa: TC001 - evaluated by Dishka.
    ResultScheduleService,
)
from scheduletelegrambot.settings import Settings  # noqa: TC001 - evaluated by Dishka.

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
@inject
async def handle_schedule(  # noqa: PLR0913, PLR0917
    message: Message,
    parser_factory: FromDishka[ParserFactory],
    user: UserModel,
    result_schedules: FromDishka[ResultScheduleService],
    default_schedules: FromDishka[DefaultScheduleService],
    settings: FromDishka[Settings],
):
    group = user.group
    if group is None or user.group_id is None:
        await message.answer("Сначала выберите группу")
        return
    week = parser_factory.get_week(group.global_shift)

    schedule = await get_schedule(
        user.group_id,
        result_schedules,
        default_schedules,
        week.weekday,
        week.shift,
    )
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(
        schedule,
        reply_markup=get_main_kb(user.telegram_id, settings.bot.admin_ids),
    )


@router.message(F.text.lower().contains("предыдущее"))
@inject
async def handle_previous_schedule(  # noqa: PLR0913, PLR0917
    message: Message,
    parser_factory: FromDishka[ParserFactory],
    user: UserModel,
    result_schedules: FromDishka[ResultScheduleService],
    default_schedules: FromDishka[DefaultScheduleService],
    settings: FromDishka[Settings],
):
    group = user.group
    if group is None or user.group_id is None:
        await message.answer("Сначала выберите группу")
        return
    week = parser_factory.get_week(group.global_shift)

    previous_weekday = week.get_previous_weekday()
    previous_shift = week.get_previous_shift()

    schedule = await get_schedule(
        user.group_id,
        result_schedules,
        default_schedules,
        previous_weekday,
        previous_shift,
    )
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(
        schedule,
        reply_markup=get_main_kb(user.telegram_id, settings.bot.admin_ids),
    )


@router.message(F.text.lower().contains("следующее"))
@inject
async def handle_next_schedule(
    message: Message,
    parser_factory: FromDishka[ParserFactory],
    user: UserModel,
    default_schedules: FromDishka[DefaultScheduleService],
    settings: FromDishka[Settings],
):
    group = user.group
    if group is None or user.group_id is None:
        await message.answer("Сначала выберите группу")
        return
    week = parser_factory.get_week(group.global_shift)

    next_weekday = week.get_next_weekday()
    next_shift = week.get_next_shift()

    schedule = await get_default_schedule(
        user.group_id, default_schedules, next_weekday, next_shift
    )
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(
        schedule,
        reply_markup=get_main_kb(user.telegram_id, settings.bot.admin_ids),
    )


async def get_schedule(
    group_id: int,
    result_schedules: ResultScheduleService,
    default_schedules: DefaultScheduleService,
    weekday: int,
    shift: int,
) -> str:
    result_schedule_data = await result_schedules.get(weekday, group_id)
    if result_schedule_data is not None and result_schedule_data.data_lessons:
        result_schedule = result_schedule_data.data_lessons + "\n"
        return str(ScheduleView.verified(result_schedule))

    return await get_default_schedule(group_id, default_schedules, weekday, shift)


async def get_default_schedule(
    group_id: int, default_schedules: DefaultScheduleService, weekday: int, shift: int
) -> str:
    default_schedule_data = await default_schedules.get(weekday, shift, group_id)
    if default_schedule_data is None or not default_schedule_data.data_lessons:
        return str(ScheduleView.missing())

    default_schedule = build_default_schedule(default_schedule_data.data_lessons)
    default_schedule = format_schedule(default_schedule, weekday, shift) + "\n"

    return str(ScheduleView.without_verification(default_schedule))


def build_default_schedule(default_schedule: str) -> list[Lesson]:
    return list(generate_default_schedule(default_schedule))
