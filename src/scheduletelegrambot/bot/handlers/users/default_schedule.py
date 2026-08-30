from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from scheduletelegrambot.bot.keyboards.users.inline.default_schedule_kb import (
    get_default_schedule_kb,
)
from scheduletelegrambot.bot.views.schedule import DefaultScheduleView
from scheduletelegrambot.components.formatters.message import (
    format_default_schedules,
)
from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.enums import WeekType
from scheduletelegrambot.services.default_schedule import (
    DefaultScheduleService,
)
from scheduletelegrambot.utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_SCHEDULE.value)
async def handle_default_schedule(callback_query: CallbackQuery):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    await message.answer(
        "Выберите на какой тип недели хотите узнать расписание",
        reply_markup=get_default_schedule_kb(),
    )


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_NUMERATOR_SCHEDULE.value)
async def handle_default_numerator_schedule(
    callback_query: CallbackQuery,
    user: UserModel,
    default_schedules: FromDishka[DefaultScheduleService],
):
    message = callback_query.message
    if not isinstance(message, Message) or user.group_id is None:
        return
    default_schedule_text = await get_default_schedule(
        user.group_id, default_schedules, WeekType.NUMERATOR
    )
    await message.answer(default_schedule_text)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_DENOMINATOR_SCHEDULE.value)
async def handle_default_denominator_schedule(
    callback_query: CallbackQuery,
    user: UserModel,
    default_schedules: FromDishka[DefaultScheduleService],
):
    message = callback_query.message
    if not isinstance(message, Message) or user.group_id is None:
        return
    default_schedule_text = await get_default_schedule(
        user.group_id, default_schedules, WeekType.DENOMINATOR
    )
    await message.answer(default_schedule_text)


async def get_default_schedule(
    group_id: int, default_schedules: DefaultScheduleService, week_type: WeekType
) -> str:
    default_schedule_data = await default_schedules.list_for_group(group_id, week_type)
    default_schedule = format_default_schedules(default_schedule_data, week_type)

    return str(DefaultScheduleView(week_type.value, default_schedule))
