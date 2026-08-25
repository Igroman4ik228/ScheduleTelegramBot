from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from scheduletelegrambot.bot.keyboards.admins.inline.subscribe.subscribe_kb import (
    get_subscribe_kb,
)
from scheduletelegrambot.bot.views.admin import AdminPanelView
from scheduletelegrambot.utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.SUBSCRIBE.value)
async def handle_subscribe(callback_query: CallbackQuery):
    if not isinstance(callback_query.message, Message):
        return
    await callback_query.message.edit_text(
        str(AdminPanelView.subscriptions()), reply_markup=get_subscribe_kb()
    )
