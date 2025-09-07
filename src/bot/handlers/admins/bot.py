from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.admins.inline.bot.bot_kb import get_bot_kb
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.BOT.value)
async def handle_bot(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Панель управления ботом", reply_markup=get_bot_kb()
    )
