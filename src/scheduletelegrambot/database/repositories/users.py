from typing import TYPE_CHECKING

from cashews import NOT_NONE

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.database.repositories.base import (
    DEFAULT_LIMIT,
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    @cache(
        ttl="3m",
        key=f"{CACHE_KEY_PREFIX}:user:{{telegram_id}}",
        tags=("user:{telegram_id}",),
        condition=NOT_NONE,
        lock=True,
    )
    async def get(self, telegram_id: int) -> UserModel | None:
        return await self.get_one(UserModel.telegram_id == telegram_id)

    @cache(
        ttl="3m",
        key=f"{CACHE_KEY_PREFIX}:user:{{telegram_id}}:group",
        tags=("user:{telegram_id}",),
        condition=NOT_NONE,
        lock=True,
    )
    async def get_with_group(self, telegram_id: int) -> UserModel | None:
        return await self.get_one(UserModel.telegram_id == telegram_id, options=(UserModel.group,))

    @cache(
        ttl="3m",
        key=f"{CACHE_KEY_PREFIX}:user:{{telegram_id}}:full",
        tags=("user:{telegram_id}",),
        condition=NOT_NONE,
        lock=True,
    )
    async def get_with_all(self, telegram_id: int) -> UserModel | None:
        return await self.get_one(
            UserModel.telegram_id == telegram_id,
            options=(
                UserModel.group,
                UserModel.subscribe,
            ),
        )

    async def get_many_with_all(self, limit: int = DEFAULT_LIMIT) -> list[UserModel]:
        return await self.get_many(
            options=(
                UserModel.group,
                UserModel.subscribe,
            ),
            limit=limit,
        )

    async def update_subscribe(
        self, user: UserModel, subscribe_id: int, subscribe_end_time: datetime
    ) -> UserModel:
        user.subscribe_id = subscribe_id
        user.subscribe_end_time = subscribe_end_time

        return await self.update(user)

    async def create(self, **values: object) -> UserModel:
        instance = await super().create(**values)

        await self._invalidate(instance.telegram_id)

        return instance

    async def update(self, instance: UserModel) -> UserModel:
        merged = await super().update(instance)

        await self._invalidate(instance.telegram_id)

        return merged

    async def delete(self, instance: UserModel) -> None:
        telegram_id = instance.telegram_id
        await super().delete(instance)
        await self._invalidate(telegram_id)

    async def _invalidate(self, telegram_id: int) -> None:
        await invalidate_tags(self.session, f"user:{telegram_id}")
