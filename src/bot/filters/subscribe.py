from aiogram.filters import Filter
from aiogram.types import Message

from database.models import UserModel


class SubscribeFilter(Filter):

    async def __call__(self, message: Message, **data) -> bool:
        user: UserModel = data.get("user")
        return user.subscribe_id is not None
