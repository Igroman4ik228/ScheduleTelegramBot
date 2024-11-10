from aiogram import F, Router, html
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.default_schedule_kb import get_default_schedule_kb
from database.models.users import UserModel
from database.repository import Repository
from services.formatter_service.message import format_default_schedules
from utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_SCHEDULE.value)
async def handle_default_schedule(callback_query: CallbackQuery):
    await callback_query.message.answer("Выберите на какой тип недели хотите узнать расписание",
                                        reply_markup=get_default_schedule_kb())


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_NUMERATOR_SCHEDULE.value)
async def handle_default_numerator_schedule(callback_query: CallbackQuery,
                                            user: UserModel, repository: Repository):
    default_schedule_repo = repository.default_schedule
    default_numerator_schedules_data = await default_schedule_repo.get_all(group_id=user.group_id)

    default_numerator_schedule = html.blockquote("Расписание на числитель")
    default_numerator_schedule += format_default_schedules(
        default_numerator_schedules_data
    )
    await callback_query.message.answer(default_numerator_schedule)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_DENOMINATOR_SCHEDULE.value)
async def handle_default_denominator_schedule(callback_query: CallbackQuery,
                                              user: UserModel, repository: Repository):
    default_schedule_repo = repository.default_schedule
    default_denominator_schedules_data = await default_schedule_repo.get_all(group_id=user.group_id)

    default_denominator_schedule = html.blockquote("Расписание на знаменатель")
    default_denominator_schedule += format_default_schedules(
        default_denominator_schedules_data
    )
    await callback_query.message.answer(default_denominator_schedule)
