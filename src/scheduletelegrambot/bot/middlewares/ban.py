from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from aiogram.types import TelegramObject

    from scheduletelegrambot.database.models.users import UserModel


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: UserModel = data["user"]
        if user.is_ban:
            return None

        return await handler(event, data)
