from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.default_schedule_kb import get_default_schedule_kb
from database.repository import Repository
from utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.WRITE_DEFAULT_SCHEDULE.value)
async def handle_default_schedule(callback_query: CallbackQuery):
    await callback_query.message.answer("Выберите какое стандартное расписание хотите узнать",
                                        reply_markup=get_default_schedule_kb())
