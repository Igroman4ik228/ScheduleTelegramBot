from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from dishka import AsyncContainer  # noqa: TC002 - required by Dishka at runtime.
from dishka.integrations.aiogram import CONTAINER_NAME

from scheduletelegrambot.database.repository import Repository

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from aiogram.types import TelegramObject


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        container: AsyncContainer = data[CONTAINER_NAME]
        data["repository"] = await container.get(Repository)
        return await handler(event, data)
