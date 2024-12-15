from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.filters.admin import AdminFilter
from bot.keyboards.admins.inline.user_kb import get_user_kb
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.USER.value, AdminFilter())
async def handle_choose_department(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Панель управления пользователями",
                                           reply_markup=get_user_kb())
