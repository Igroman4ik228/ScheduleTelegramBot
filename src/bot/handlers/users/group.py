from aiogram import Router
from aiogram.types import Message

from bot.filters.group import GroupFilter
from bot.keyboards.inline.department_kb import get_department_kb

router = Router(name=__name__)


@router.message(~GroupFilter())
async def handle_check_group(message: Message):
    await message.answer("Выберите отделение пожалуйста",
                         reply_markup=await get_department_kb())
