from aiogram import F, Router
from aiogram.types import Message

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message):
    pass


@ router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message):
    pass


@ router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message):
    pass
