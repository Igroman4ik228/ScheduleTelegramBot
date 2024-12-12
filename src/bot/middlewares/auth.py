from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.types.user import User

from database.models.users import UserModel
from database.redis.repositories import clear_cache
from database.repositories.users import UserRepository
from database.repository import Repository


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
    ) -> Any:
        repository: Repository = data["repository"]
        user_rep = repository.users

        user = data["event_from_user"]
        existing_user = await user_rep.get_with_group(user.id)
        if existing_user:
            data["user"] = existing_user
            return await handler(event, data)

        await clear_cache(user_rep.get_with_group, user_rep, user.id)
        new_user = await self._create_user(user, repository)
        data["user"] = new_user

        return await handler(event, data)

    async def _create_user(self, tg_user: User, repository: Repository) -> UserModel:
        subscribes = await repository.subscribes.get_all(price=0)
        subscribe_end_time = datetime.now() + timedelta(
            days=subscribes[0].duration_days
        )

        user_rep = repository.users
        new_user = await user_rep.create(
            first_name=tg_user.first_name,
            user_name=tg_user.username,
            telegram_id=tg_user.id,
            last_name=tg_user.last_name,
            is_bot=tg_user.is_bot,
            is_premium=tg_user.is_premium,
            subscribe_id=subscribes[0].id,
            subscribe_end_time=subscribe_end_time)
        if new_user is None:
            raise ValueError(f"Failed to create user: {tg_user}")

        return new_user
