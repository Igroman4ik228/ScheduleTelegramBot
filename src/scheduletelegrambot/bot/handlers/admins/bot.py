from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from scheduletelegrambot.bot.keyboards.admins.inline.bot.bot_kb import (
    get_bot_kb,
)
from scheduletelegrambot.bot.views.admin import AdminPanelView
from scheduletelegrambot.utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.BOT.value)
async def handle_bot(callback_query: CallbackQuery):
    if isinstance(callback_query.message, Message):
        await callback_query.message.edit_text(str(AdminPanelView.bot()), reply_markup=get_bot_kb())
