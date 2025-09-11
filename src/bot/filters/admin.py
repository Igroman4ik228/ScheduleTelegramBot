from aiogram.filters import Filter
from aiogram.types import Message

from helpers.user_validate import is_admin


class AdminFilter(Filter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        user = message.from_user
        if user is None:
            return False

        return is_admin(user.id, self.admin_ids)
