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

    async def update(self, user: UserModel):
        self.clear_cache(user.telegram_id)
        await self.session.merge(user)

    async def delete(self, user: UserModel):
        self.clear_cache(user.telegram_id)
        await self.session.delete(user)

    async def clear_cache(self, telegram_id: int):
        clear_cache(self.get, telegram_id)
        clear_cache(self.get_with_group, telegram_id)
        clear_cache(self.get_with_all, telegram_id)
