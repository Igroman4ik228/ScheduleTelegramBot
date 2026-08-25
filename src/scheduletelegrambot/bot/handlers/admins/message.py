from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from scheduletelegrambot.bot.keyboards.admins.inline.message.message_kb import (
    get_message_kb,
)
from scheduletelegrambot.bot.views.admin import AdminPanelView
from scheduletelegrambot.utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.MESSAGE.value)
async def handle_group(callback_query: CallbackQuery):
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(
        str(AdminPanelView.messages()), reply_markup=get_message_kb()
    )
