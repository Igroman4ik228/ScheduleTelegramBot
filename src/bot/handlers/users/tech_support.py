from aiogram import F, Router
from aiogram.types import Message

router = Router(name=__name__)


@router.message(F.text.lower().contains("техподдержка"))
async def handle_tech_support(message: Message):
    await message.answer("В разработке...")
