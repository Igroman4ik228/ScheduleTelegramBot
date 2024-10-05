from aiogram import Router
from aiogram.types import Message

from bot.filters.group import GroupFilter

router = Router(name=__name__)


@router.message(~GroupFilter())
async def handle_check_group(message: Message):
    await message.answer("Выберите группу, пожалуйста")
