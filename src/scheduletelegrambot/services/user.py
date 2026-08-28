from __future__ import annotations

from datetime import datetime

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.base import DEFAULT_LIMIT
from scheduletelegrambot.database.repositories.users import UserRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.schemas.user import (
    UserBaseSchema,
    UserWithAllSchema,
    UserWithGroupSchema,
)

_CACHE_TAG = "users"


class UserService:
    def __init__(self, user_repository: UserRepository, uow: UoW) -> None:
        self.user_repository = user_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="3m",
        early_ttl="2m",
        tags=(_CACHE_TAG, "user:{telegram_id}"),
        condition=NOT_NONE,
    )
    async def find(self, telegram_id: int) -> UserBaseSchema | None:
        model = await self.user_repository.get_by_telegram_id(telegram_id)
        if not model:
            return None
        return UserBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="3m",
        early_ttl="2m",
        tags=(_CACHE_TAG, "user:{telegram_id}"),
        condition=NOT_NONE,
    )
    async def find_with_group(self, telegram_id: int) -> UserWithGroupSchema | None:
        model = await self.user_repository.get_with_group(telegram_id)
        if not model:
            return None
        return UserWithGroupSchema.model_validate(model)

    @noself(cache.early)(
        ttl="3m",
        early_ttl="2m",
        tags=(_CACHE_TAG, "user:{telegram_id}"),
        condition=NOT_NONE,
    )
    async def find_with_all(self, telegram_id: int) -> UserWithAllSchema | None:
        model = await self.user_repository.get_with_all(telegram_id)
        if not model:
            return None
        return UserWithAllSchema.model_validate(model)

    async def list_all(self) -> list[UserBaseSchema]:
        models = await self.user_repository.list_all()
        return [UserBaseSchema.model_validate(model) for model in models]

    async def list_all_by_group_id(self, group_id: int) -> list[UserBaseSchema]:
        models = await self.user_repository.list_by_group_id(group_id)
        return [UserBaseSchema.model_validate(model) for model in models]

    async def list_all_without_group(self) -> list[UserBaseSchema]:
        models = await self.user_repository.list_without_group()
        return [UserBaseSchema.model_validate(model) for model in models]

    async def list_notification_recipients(self) -> list[UserWithGroupSchema]:
        models = await self.user_repository.list_notification_recipients()
        return [UserWithGroupSchema.model_validate(model) for model in models]

    async def list_all_with_subscribe(self, limit: int = DEFAULT_LIMIT) -> list[UserWithAllSchema]:
        models = await self.user_repository.list_with_subscribe(limit)
        return [UserWithAllSchema.model_validate(model) for model in models]

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
    ) -> UserBaseSchema:
        model = await self.user_repository.create(
            first_name=first_name,
            last_name=last_name,
            user_name=user_name,
            telegram_id=telegram_id,
            is_bot=is_bot,
            is_premium=is_premium,
            subscribe_id=subscribe_id,
            subscribe_end_time=subscribe_end_time,
        )

        await self.uow.commit()

        await cache.delete_tags(f"user:{telegram_id}")

        return UserBaseSchema.model_validate(model)

    async def update_group(self, telegram_id: int, group_id: int) -> bool:
        updated = await self.user_repository.execute_update_group(telegram_id, group_id)
        if updated:
            await self.uow.commit()
            await cache.delete_tags(f"user:{telegram_id}")
        return updated

    async def update_ban(self, telegram_id: int, *, is_ban: bool) -> bool:
        updated = await self.user_repository.execute_update_ban(telegram_id, is_ban)
        if updated:
            await self.uow.commit()
            await cache.delete_tags(f"user:{telegram_id}")
        return updated

    async def update_notify(self, telegram_id: int, *, is_notify: bool) -> bool:
        updated = await self.user_repository.execute_update_notify(telegram_id, is_notify)
        if updated:
            await self.uow.commit()
            await cache.delete_tags(f"user:{telegram_id}")
        return updated

    async def update_time_shown(self, telegram_id: int, *, is_time_shown: bool) -> bool:
        updated = await self.user_repository.execute_update_time_shown(telegram_id, is_time_shown)
        if updated:
            await self.uow.commit()
            await cache.delete_tags(f"user:{telegram_id}")
        return updated

    async def update_subscribe(
        self, telegram_id: int, subscribe_id: int | None, subscribe_end_time: datetime | None
    ) -> bool:
        updated = await self.user_repository.execute_update_subscribe(
            telegram_id, subscribe_id, subscribe_end_time
        )
        if updated:
            await self.uow.commit()

            await cache.delete_tags(f"user:{telegram_id}")
        return updated
