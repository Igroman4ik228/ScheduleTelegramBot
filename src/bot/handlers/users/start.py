from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.reply.main_kb import get_main_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    welcome_message = (f"Здравствуйте {html.quote(user_full_name)}.\n"
                       "Вас приветствует элитный бот расписания ЯГК.🥇")

    await message.answer(welcome_message, reply_markup=get_main_kb(user_id))
