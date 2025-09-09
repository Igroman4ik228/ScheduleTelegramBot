from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.cache.repositories import CacheRepositoryService
from database.db import IDatabase
from database.repository import CachedRepository


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        db: IDatabase = data["db"]
        cache_service: CacheRepositoryService = data["cache_service"]
        async with db.get_session() as session:
            data["repository"] = CachedRepository(session, cache_service)
            return await handler(event, data)
