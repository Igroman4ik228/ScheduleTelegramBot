from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware

from database.repository import CachedRepository

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable

    from aiogram.types import TelegramObject

    from database.db import DatabaseAlchemy
    from helpers.cache import CacheHelper


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db: DatabaseAlchemy = data["db"]
        cache_service: CacheHelper = data["cache_service"]
        async with db.get_session() as session:
            data["repository"] = CachedRepository(session, cache_service)
            return await handler(event, data)
