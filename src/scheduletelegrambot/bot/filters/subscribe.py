from typing import TYPE_CHECKING

from aiogram.filters import Filter

from scheduletelegrambot.schemas.user import UserBaseSchema

if TYPE_CHECKING:
    from aiogram.types import Message


class SubscribeFilter(Filter):
    async def __call__(self, _message: Message, **data) -> bool:
        user = data.get("user")
        return isinstance(user, UserBaseSchema) and user.subscribe_id is not None
