from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from database.redis.repositories import clear_cache
from database.repository import Repository


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any]
    ) -> Any:
        user = event.from_user
        repository: Repository = data["repository"]
        user_rep = repository.users

        existing_user = await user_rep.get_with_group(user.id)
        if existing_user:
            data["user"] = existing_user
            return await handler(event, data)

        await clear_cache(user_rep.get_with_group, self, user.id)
        new_user = await user_rep.create(
            first_name=user.first_name,
            user_name=user.username,
            telegram_id=user.id,
            last_name=user.last_name,
            is_bot=user.is_bot,
            is_premium=user.is_premium
        )

        if new_user is not None:
            self.logger.info(f"New user registration: {repr(new_user)}")
            data["user"] = new_user

        return await handler(event, data)
