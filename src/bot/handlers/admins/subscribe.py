from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.filters.admin import AdminFilter
from bot.keyboards.admins.inline.subscribe_kb import get_subscribe_kb
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.SUBSCRIBE.value, AdminFilter())
async def handle_subscribe(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Панель управления подписками",
                                           reply_markup=get_subscribe_kb())
