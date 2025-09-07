from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.models.users import UserModel


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user: UserModel = data["user"]
        if user.is_ban:
            return None
        return await handler(event, data)
