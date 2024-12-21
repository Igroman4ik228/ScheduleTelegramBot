from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.admins.inline.group.group_kb import get_group_kb
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


@router.callback_query(F.data == CallbackDataAdmin.GROUP.value)
async def handle_group(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Панель управления группами",
                                           reply_markup=get_group_kb())
