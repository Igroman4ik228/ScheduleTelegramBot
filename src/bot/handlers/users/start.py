from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.inline.subscribe_kb import get_subscribe_kb
from database.repository import Repository

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message,
                       repository: Repository):
    user_full_name = message.from_user.full_name
    welcome_message = (f"Здравствуйте {html.quote(user_full_name)}.\n"
                       "Вас приветствует элитный бот расписания ЯГК.🥇")
    await message.answer(welcome_message)

    subscribes = await repository.subscribes.get_all()
    await message.answer("Выберите подписку пожалуйста",
                         reply_markup=get_subscribe_kb(subscribes))
