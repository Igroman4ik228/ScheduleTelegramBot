from aiogram import F, Router
from aiogram.types import Message

from database.repositories.result_schedule import ResultScheduleRepository
from database.repositories.users import UserRepository

router = Router(name=__name__)
user_rep = UserRepository()
result_rep = ResultScheduleRepository()


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message):
    # user = await user_rep.get(message.from_user.id)
    # await message.answer(f"{user.group_id} Расписание")
    pass


@ router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message):
    pass


@ router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message):
    pass
