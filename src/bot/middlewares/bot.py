from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Dict

    from aiogram.types import TelegramObject

    from database.models import UserModel


class BotMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: UserModel = data["user"]
        if user.is_bot:
            return None
        return await handler(event, data)
