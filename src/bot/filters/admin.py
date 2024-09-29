from aiogram.filters import Filter
from aiogram.types import Message

from utils.different import is_admin


class AdminFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        if user_id is None:
            return False

        return is_admin(user_id)
