from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.admins.inline.panel_kb import get_admin_panel_kb

router = Router(name=__name__)


@router.message(F.text.lower().contains("админ панель"))
async def handle_panel(message: Message):
    await message.answer("Панель администратора",
                         reply_markup=get_admin_panel_kb())
