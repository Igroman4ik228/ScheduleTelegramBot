from aiogram import F, Router, html
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.department_kb import get_department_kb
from bot.keyboards.inline.group_kb import get_group_kb
from bot.keyboards.reply.main_kb import get_main_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message):
    user_full_name = message.from_user.full_name
    welcome_message = (f"Здравствуйте {html.quote(user_full_name)}.\n"
                       "Вас приветствует элитный бот расписания ЯГК.🥇")
    await message.answer(welcome_message)

    await message.answer("Выберите отделение",
                         reply_markup=await get_department_kb())


@router.callback_query(F.data.contains("Department"))
async def handle_department(callback_query: CallbackQuery):
    department = callback_query.data.split(":")[1]
    await callback_query.message.answer(f"Вы выбрали отделение {department}")
    await callback_query.message.edit_text("Выберите группу",
                                           reply_markup=await get_group_kb())


@router.callback_query(F.data.contains("Group"))
async def handle_group(callback_query: CallbackQuery):
    group = callback_query.data.split(":")[1]

    await callback_query.message.edit_text("Спасибо за выбор группы 🥳")

    user_id = callback_query.from_user.id
    await callback_query.message.answer(f"Вы выбрали группу {group}",
                                        reply_markup=get_main_kb(user_id))
