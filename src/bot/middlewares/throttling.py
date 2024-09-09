from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache

from config import settings


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = settings.RATE_LIMIT) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.chat.id in self.cache:
            return None
        self.cache[event.chat.id] = None
        return await handler(event, data)
