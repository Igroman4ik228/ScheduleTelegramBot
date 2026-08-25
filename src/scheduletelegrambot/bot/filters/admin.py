from typing import TYPE_CHECKING

from aiogram.filters import Filter

from scheduletelegrambot.helpers.user_validate import is_admin

if TYPE_CHECKING:
    from aiogram.types import Message


class AdminFilter(Filter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        user = message.from_user
        if user is None:
            return False

        return is_admin(user.id, self.admin_ids)
