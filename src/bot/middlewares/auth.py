from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.types.user import User

from database.models.users import UserModel
from database.redis.repositories import clear_cache
from database.repositories.subscribes import SubscribeRepository
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
        tg_user: User = data["event_from_user"]

        existing_user = await self._get_user(tg_user.id, repository.users)
        if existing_user:
            data["user"] = existing_user
            return await handler(event, data)

        new_user = await self._create_user(
            tg_user,
            repository.subscribes,
            repository.users
        )
        data["user"] = new_user
        return await handler(event, data)

    async def _get_user(
        self,
        user_id: int,
        user_repo: UserRepository
    ) -> UserModel | None:
        user = await user_repo.get(
            user_id,
            "group", "subscribe"
        )
        if user is None:
            await clear_cache(
                user_repo.get,
                user_repo,
                user_id,
                "group", "subscribe"
            )
        return user

    async def _create_user(
        self,
        tg_user: User,
        subscribe_repo: SubscribeRepository,
        user_repo: UserRepository
    ) -> UserModel:
        subscribes = await subscribe_repo.get_all(price=0)
        subscribe_end_time = datetime.now() + timedelta(
            days=subscribes[0].duration_days
        )

        new_user = await user_repo.create(
            first_name=tg_user.first_name,
            user_name=tg_user.username,
            telegram_id=tg_user.id,
            last_name=tg_user.last_name,
            is_bot=tg_user.is_bot,
            is_premium=tg_user.is_premium,
            subscribe_id=subscribes[0].id,
            subscribe_end_time=subscribe_end_time
        )

        if new_user is None:
            raise ValueError(f"Failed to create user: {tg_user}")

        self.logger.info(
            f"Successfully registered new user: {tg_user.username}"
        )
        return new_user
