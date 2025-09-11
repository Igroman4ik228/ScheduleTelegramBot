from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from cachetools import TTLCache

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Dict

    from aiogram.types import (
        TelegramObject,
    )


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: int = data["event_from_user"].id
        if user_id in self.cache:
            return None

        self.cache[user_id] = None
        return await handler(event, data)
