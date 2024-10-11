from aiogram import F, Router
from aiogram.types import Message
from injector import Injector

from bot.filters.admin import AdminFilter
from main import AppModule, injector
from parser_service.week import Week

router = Router(name=__name__)


@router.message(F.text.lower().contains("админ панель"), AdminFilter())
async def handle_panel(message: Message):
    await message.answer("Админ панель")
