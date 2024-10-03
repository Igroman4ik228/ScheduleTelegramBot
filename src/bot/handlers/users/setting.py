from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from utils import constants

router = Router(name=__name__)


@router.message(F.text.lower().contains("настройки"))
async def handle_settings(message: Message):
    await message.answer("Настройки")


@router.message(F.data == constants.TOGGLE_NOTIFICATION)
async def handle_notification(callback_query: CallbackQuery):
    pass
