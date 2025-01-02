from aiogram import F, Router, html
from aiogram.types import CallbackQuery

from bot.keyboards.users.inline.default_schedule_kb import \
    get_default_schedule_kb
from database.models import UserModel
from database.repository import Repository
from helpers.algorithm import get_key
from services.formatter_service.message import format_default_schedules
from utils.constants import WEEK_SCHEDULE_MAPPING, CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_SCHEDULE.value)
async def handle_default_schedule(callback_query: CallbackQuery):
    await callback_query.message.answer("Выберите на какой тип недели хотите узнать расписание",
                                        reply_markup=get_default_schedule_kb())


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_NUMERATOR_SCHEDULE.value)
async def handle_default_numerator_schedule(callback_query: CallbackQuery,
                                            user: UserModel, repository: Repository):
    default_schedule_text = await get_default_schedule(
        user.group_id, repository, shift=1
    )
    await callback_query.message.answer(default_schedule_text)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_DENOMINATOR_SCHEDULE.value)
async def handle_default_denominator_schedule(callback_query: CallbackQuery,
                                              user: UserModel, repository: Repository):
    default_schedule_text = await get_default_schedule(
        user.group_id, repository, shift=2
    )
    await callback_query.message.answer(default_schedule_text)


async def get_default_schedule(group_id: int, repository: Repository, shift: int) -> str:
    default_schedule_repo = repository.default_schedule
    default_schedule_data = await default_schedule_repo.get_all(shift=shift,
                                                                group_id=group_id)
    shift_name = get_key(WEEK_SCHEDULE_MAPPING, shift)
    default_schedule_header = html.blockquote(f"Расписание на {shift_name}")
    default_schedule = format_default_schedules(
        default_schedule_data, shift
    )

    return default_schedule_header + default_schedule
