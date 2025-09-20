from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel
from database.repositories.base_copy import DEFAULT_LIMIT, BaseRepositoryAlchemy
from helpers.cache import Cacheable, CacheHelper, cached, clear_cache


class UserRepository(BaseRepositoryAlchemy[UserModel], Cacheable):
    def __init__(self, session: AsyncSession, cache_helper: CacheHelper):
        BaseRepositoryAlchemy.__init__(self, session, UserModel)
        Cacheable.__init__(self, cache_helper)

    @cached()
    async def get(self, telegram_id: int) -> UserModel | None:
        return await self._get(UserModel.telegram_id == telegram_id)

    @cached()
    async def get_with_group(self, telegram_id: int) -> UserModel | None:
        return await self._get(
            UserModel.telegram_id == telegram_id, options=(UserModel.group,)
        )

    @cached()
    async def get_with_all(self, telegram_id: int) -> UserModel | None:
        return await self._get(
            UserModel.telegram_id == telegram_id,
            options=(
                UserModel.group,
                UserModel.subscribe,
            ),
        )

    async def get_many_with_all(self, limit: int = DEFAULT_LIMIT):
        return await self._get_many(
            options=(
                UserModel.group,
                UserModel.subscribe,
            ),
            limit=limit,
        )

    async def update_subscribe(
        self, user: UserModel, subscribe_id: int, subscribe_end_time: datetime
    ):
        user.subscribe_id = subscribe_id
        user.subscribe_end_time = subscribe_end_time

        await self.update(user)

    async def update(self, instance: UserModel) -> UserModel:
        await self.clear_cache(instance.telegram_id)
        return await self.session.merge(instance)

    async def delete(self, instance: UserModel):
        await self.clear_cache(instance.telegram_id)
        await self.session.delete(instance)

    async def clear_cache(self, telegram_id: int):
        await clear_cache(self.get, telegram_id)
        await clear_cache(self.get_with_group, telegram_id)
        await clear_cache(self.get_with_all, telegram_id)
