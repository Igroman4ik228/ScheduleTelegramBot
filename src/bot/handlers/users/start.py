from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.inline.subscribe_kb import get_subscribe_kb
from database.repository import Repository

router = Router(name=__name__)

TITLE = "Приветствие"


@router.message(CommandStart())
async def handle_start(message: Message):
    user_full_name = message.from_user.full_name
    welcome_message = (f"Здравствуйте {html.quote(user_full_name)}.\n"
                       "Вас приветствует элитный бот расписания ЯГК.🥇")
    await message.answer(welcome_message)
