from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel
from database.redis.repositories import cached, clear_cache
from database.repositories import GroupRepository
from database.repositories.base import BaseRepositoryAlchemy
from utils.constants import CacheTTL


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession):
        self.logger = getLogger(self.__class__.__name__)
        super().__init__(session, UserModel)
        self.group_repo = GroupRepository(session)

    async def create(
            self,
            first_name: str,
            user_name: str,
            telegram_id: int,
            group_name: str = None,
            **kwargs
    ) -> UserModel | None:
        group_id = None
        if group_name:
            group = await self.group_repo.get_by_name(group_name)
            if group is None:
                self.logger.debug(
                    f"Group {group_name} not found for create"
                )
                return
            group_id = group.id

        return await super().create(
            first_name=first_name,
            user_name=user_name,
            telegram_id=telegram_id,
            group_id=group_id,
            **kwargs
        )

    @cached(ttl=CacheTTL.USER.value)
    async def get(self, telegram_id: int, *options) -> UserModel | None:
        return await super().get(telegram_id=telegram_id, *options)

    async def update(self, instance: UserModel):
        await super().update(instance)
        await self._clear_user_cache(instance.telegram_id)

    async def delete(self, telegram_id: int):
        await super().delete(telegram_id=telegram_id)
        await self._clear_user_cache(telegram_id)

    async def _clear_user_cache(self, telegram_id):
        await clear_cache(self.get, self, telegram_id, "group", "subscribe")
        await clear_cache(self.get, self, telegram_id, "group")
        await clear_cache(self.get, self, telegram_id)
