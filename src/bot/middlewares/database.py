from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware

from database.uow import CachedUoW

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
        cache_helper: CacheHelper = data["cache_helper"]
        async with CachedUoW(db.sessionmaker, cache_helper) as uow:
            data["uow"] = uow
            return await handler(event, data)
