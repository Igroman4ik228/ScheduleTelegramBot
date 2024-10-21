from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.default_schedule_kb import get_default_schedule_kb
from database.models.users import UserModel
from database.repository import Repository
from services.parser_service.formatter import ScheduleFormatter, add_html_tag
from utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_SCHEDULE.value)
async def handle_default_schedule(callback_query: CallbackQuery):
    await callback_query.message.answer("Выберите на какой тип недели хотите узнать расписание",
                                        reply_markup=get_default_schedule_kb())


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_NUMERATOR_SCHEDULE.value)
async def handle_default_numerator_schedule(callback_query: CallbackQuery,
                                            user: UserModel, repository: Repository):
    default_numerator_schedule_list = await repository.default_schedule.get_all(group_id=user.group_id)

    default_numerator_schedule = add_html_tag(
        "Расписание на числитель",
        "blockquote"
    )
    await callback_query.message.answer(default_numerator_schedule)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_DENOMINATOR_SCHEDULE.value)
async def handle_default_denominator_schedule(callback_query: CallbackQuery,
                                              user: UserModel, repository: Repository):
    default_denominator_schedule_list = await repository.default_schedule.get_all(group_id=user.group_id)

    default_denominator_schedule = add_html_tag(
        "Расписание на знаменатель",
        "blockquote"
    )
    await callback_query.message.answer(default_denominator_schedule)
