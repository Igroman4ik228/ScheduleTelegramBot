from __future__ import annotations

from datetime import UTC, datetime, timedelta
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from dishka.integrations.aiogram import CONTAINER_NAME

from scheduletelegrambot.helpers.text import quote_html_range
from scheduletelegrambot.schemas.user import UserWithAllSchema
from scheduletelegrambot.services.subscribe import SubscribeService
from scheduletelegrambot.services.user import UserService

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from aiogram.types import TelegramObject
    from aiogram.types.user import User as AiogramUser
    from dishka import AsyncContainer


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        aiogram_user: AiogramUser | None = data.get("event_from_user")
        if aiogram_user is None:
            return await handler(event, data)

        container: AsyncContainer = data[CONTAINER_NAME]
        users = await container.get(UserService)
        existing_user = await users.find_with_all(aiogram_user.id)

        if existing_user:
            data["user"] = existing_user
            return await handler(event, data)

        subscribes = await container.get(SubscribeService)
        data["user"] = await self._create_user(aiogram_user, users, subscribes)
        return await handler(event, data)

    async def _create_user(
        self,
        tg_user: AiogramUser,
        users: UserService,
        subscribes: SubscribeService,
    ) -> UserWithAllSchema:
        available_subscribes = await subscribes.list_all_by_price(0)
        if not available_subscribes:
            raise ValueError("No free subscribes available for new users")

        trail_subscribe = available_subscribes[0]
        subscribe_end_time = datetime.now(UTC) + timedelta(days=trail_subscribe.duration_days)

        first_name, last_name = quote_html_range([tg_user.first_name, tg_user.last_name])

        new_user = await users.create(
            first_name=first_name or "",
            last_name=last_name,
            user_name=tg_user.username,
            telegram_id=tg_user.id,
            is_bot=tg_user.is_bot,
            is_premium=tg_user.is_premium,
            subscribe_id=trail_subscribe.id,
            subscribe_end_time=subscribe_end_time,
        )

        # Get must be called after create to ensure relations are loaded
        new_user = await users.find_with_all(new_user.telegram_id)

        if new_user is None:
            raise ValueError("Failed to create new user")

        self.logger.info("Successfully registered new user: %s", new_user)
        return new_user
