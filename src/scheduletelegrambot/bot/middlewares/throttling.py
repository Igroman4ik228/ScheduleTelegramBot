from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware

from scheduletelegrambot.cache.cashews import CACHE_KEY_PREFIX, cache

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from aiogram.types import (
        TelegramObject,
    )


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float) -> None:
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id: int = data["event_from_user"].id
        attempts = await cache.incr(
            f"{CACHE_KEY_PREFIX}:throttle:{user_id}", expire=self.rate_limit
        )
        if attempts > 1:
            return None
        return await handler(event, data)
