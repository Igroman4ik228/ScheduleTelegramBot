from aiogram.filters import Filter
from aiogram.types import Message

from database.db import sessionmaker
from database.repositories.users import UserRepository


class GroupFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        user = message.from_user
        if user is None:
            return False
        return await has_group(user.id)


async def has_group(user_id: int) -> bool:
    async with sessionmaker() as session:
        user = await UserRepository(session).get(user_id)
        if user is None:
            return False
        if user.group_id is None:
            return False
        return True
