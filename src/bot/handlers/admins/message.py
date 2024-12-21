from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.admins.inline.message.message_kb import get_message_kb
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.MESSAGE.value)
async def handle_group(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Панель управления сообщениями",
                                           reply_markup=get_message_kb())
