from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update
from cachetools import TTLCache

from utils.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = settings.RATE_LIMIT) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user_id = data["event_from_user"].id
        if user_id in self.cache:
            return None

        self.cache[user_id] = None
        return await handler(event, data)
