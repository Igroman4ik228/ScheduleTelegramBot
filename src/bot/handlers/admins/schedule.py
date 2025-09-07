from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.admins.inline.schedule.schedule_kb import get_schedule_kb
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.SCHEDULE.value)
async def handle_schedule(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Панель управления расписанием", reply_markup=get_schedule_kb()
    )
