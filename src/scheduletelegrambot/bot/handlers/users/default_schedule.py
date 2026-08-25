from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from scheduletelegrambot.bot.keyboards.users.inline.default_schedule_kb import (
    get_default_schedule_kb,
)
from scheduletelegrambot.bot.views.schedule import DefaultScheduleView
from scheduletelegrambot.components.formatters.message import (
    format_default_schedules,
)
from scheduletelegrambot.database.models import UserModel  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.helpers.algorithm import get_key
from scheduletelegrambot.services.default_schedule import (  # noqa: TC001 - evaluated by Dishka.
    DefaultScheduleService,
)
from scheduletelegrambot.utils.constants import (
    WEEK_SCHEDULE_MAPPING,
    CallbackData,
)

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
@inject
async def handle_default_numerator_schedule(
    callback_query: CallbackQuery,
    user: UserModel,
    default_schedules: FromDishka[DefaultScheduleService],
):
    message = callback_query.message
    if not isinstance(message, Message) or user.group_id is None:
        return
    default_schedule_text = await get_default_schedule(user.group_id, default_schedules, shift=1)
    await message.answer(default_schedule_text)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_DENOMINATOR_SCHEDULE.value)
@inject
async def handle_default_denominator_schedule(
    callback_query: CallbackQuery,
    user: UserModel,
    default_schedules: FromDishka[DefaultScheduleService],
):
    message = callback_query.message
    if not isinstance(message, Message) or user.group_id is None:
        return
    default_schedule_text = await get_default_schedule(user.group_id, default_schedules, shift=2)
    await message.answer(default_schedule_text)


async def get_default_schedule(
    group_id: int, default_schedules: DefaultScheduleService, shift: int
) -> str:
    default_schedule_data = await default_schedules.get_all_by_group_and_shift(group_id, shift)
    shift_name = get_key(WEEK_SCHEDULE_MAPPING, shift)
    default_schedule = format_default_schedules(default_schedule_data, shift)

    return str(DefaultScheduleView(shift_name, default_schedule))
