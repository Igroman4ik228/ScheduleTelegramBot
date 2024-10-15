from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.inline.department_kb import get_department_kb
from database.repository import Repository

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message,
                       repository: Repository):
    user_full_name = message.from_user.full_name
    welcome_message = (f"Здравствуйте {html.quote(user_full_name)}.\n"
                       "Вас приветствует элитный бот расписания ЯГК.🥇")
    await message.answer(welcome_message)

    departments = await repository.departments.get_all()
    await message.answer("Выберите отделение",
                         reply_markup=await get_department_kb(departments))
