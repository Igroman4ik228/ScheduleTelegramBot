from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.db import sessionmaker
from database.repository import Repository


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:

        async with sessionmaker() as session:
            data["repository"] = Repository(session)
            return await handler(event, data)
