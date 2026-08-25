from typing import TYPE_CHECKING

from aiogram.filters import Filter

if TYPE_CHECKING:
    from aiogram.types import Message

    from scheduletelegrambot.database.models import UserModel


class GroupFilter(Filter):
    async def __call__(self, _message: Message, **data) -> bool:
        user: UserModel = data["user"]
        return user.group_id is not None
