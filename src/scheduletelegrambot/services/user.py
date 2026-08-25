from __future__ import annotations

from typing import TYPE_CHECKING

from cashews import NOT_NONE

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.database.repositories.base import DEFAULT_LIMIT

if TYPE_CHECKING:
    from datetime import datetime

    from scheduletelegrambot.database.repositories.users import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    @cache(
        ttl="3m",
        key=f"{CACHE_KEY_PREFIX}:user:{{telegram_id}}",
        tags=("users", "user:{telegram_id}"),
        condition=NOT_NONE,
        lock=True,
    )
    async def get(self, telegram_id: int) -> UserModel | None:
        return await self.repository.get_one(UserModel.telegram_id == telegram_id)

    @cache(
        ttl="3m",
        key=f"{CACHE_KEY_PREFIX}:user:{{telegram_id}}:group",
        tags=("users", "user:{telegram_id}"),
        condition=NOT_NONE,
        lock=True,
    )
    async def get_with_group(self, telegram_id: int) -> UserModel | None:
        return await self.repository.get_one(
            UserModel.telegram_id == telegram_id,
            options=(UserModel.group,),
        )

    @cache(
        ttl="3m",
        key=f"{CACHE_KEY_PREFIX}:user:{{telegram_id}}:full",
        tags=("users", "user:{telegram_id}"),
        condition=NOT_NONE,
        lock=True,
    )
    async def get_with_all(self, telegram_id: int) -> UserModel | None:
        return await self.repository.get_one(
            UserModel.telegram_id == telegram_id,
            options=(UserModel.group, UserModel.subscribe),
        )

    async def get_all(self) -> list[UserModel]:
        return await self.repository.get_many()

    async def get_all_by_group_id(self, group_id: int) -> list[UserModel]:
        return await self.repository.get_many(UserModel.group_id == group_id)

    async def get_all_without_group(self) -> list[UserModel]:
        return await self.repository.get_many(UserModel.group_id.is_(None))

    async def get_notification_recipients(self) -> list[UserModel]:
        return await self.repository.get_many(
            UserModel.is_notify.is_(True),
            UserModel.is_ban.is_(False),
            UserModel.is_bot.is_(False),
            options=(UserModel.group,),
        )

    async def get_all_with_subscribe(self, limit: int = DEFAULT_LIMIT) -> list[UserModel]:
        return await self.repository.get_many(
            options=(UserModel.subscribe,),
            limit=limit,
        )

    # ruff: noqa: PLR0913
    async def create(
        self,
        *,
        first_name: str,
        last_name: str | None,
        user_name: str | None,
        telegram_id: int,
        is_bot: bool,
        is_premium: bool | None,
        subscribe_id: int,
        subscribe_end_time: datetime,
    ) -> UserModel:
        instance = await self.repository.create(
            first_name=first_name,
            last_name=last_name,
            user_name=user_name,
            telegram_id=telegram_id,
            is_bot=is_bot,
            is_premium=is_premium,
            subscribe_id=subscribe_id,
            subscribe_end_time=subscribe_end_time,
        )
        await self._invalidate_user(instance.telegram_id)
        return instance

    async def set_group(self, user: UserModel, group_id: int) -> UserModel:
        user.group_id = group_id
        return await self._update(user)

    async def set_ban(self, user: UserModel, *, is_ban: bool) -> UserModel:
        user.is_ban = is_ban
        return await self._update(user)

    async def set_notify(self, user: UserModel, *, is_notify: bool) -> UserModel:
        user.is_notify = is_notify
        return await self._update(user)

    async def set_time_shown(self, user: UserModel, *, is_time_shown: bool) -> UserModel:
        user.is_time_shown = is_time_shown
        return await self._update(user)

    async def update_subscribe(
        self, user: UserModel, subscribe_id: int | None, subscribe_end_time: datetime | None
    ) -> UserModel:
        user.subscribe_id = subscribe_id
        user.subscribe_end_time = subscribe_end_time
        return await self._update(user)

    async def _update(self, user: UserModel) -> UserModel:
        updated = await self.repository.update(user)
        await self._invalidate_user(updated.telegram_id)
        return updated

    async def _invalidate_user(self, telegram_id: int) -> None:
        await invalidate_tags(self.repository.session, f"user:{telegram_id}")
