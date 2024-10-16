from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.users import UserModel
from database.redis.repositories import (build_key_from_repo, cached,
                                         clear_cache)
from database.repositories.base import BaseRepositoryAlchemy
from database.repositories.groups import GroupRepository


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession):
        self.logger = getLogger(__name__)
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
                self.logger.warning(
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

    def _build_key(self, telegram_id: int, **kwargs) -> str:
        return build_key_from_repo(self, telegram_id, **kwargs)

    @cached(key_builder=_build_key)
    async def get(self, telegram_id: int) -> UserModel | None:
        return await super().get(telegram_id=telegram_id)

    @cached(key_builder=_build_key)
    async def get_with_group(self, telegram_id: int) -> UserModel | None:
        return await super().get_with_option("group", telegram_id=telegram_id)

    @cached(key_builder=_build_key)
    async def get_all(self, **kwargs) -> list[UserModel]:
        return await super().get_all(**kwargs)

    async def update(self, instance: UserModel):
        await super().update(instance)
        self._clear_user_cache(instance.telegram_id)

    async def delete(self, telegram_id: int):
        await super().delete(telegram_id=telegram_id)
        self._clear_user_cache(telegram_id)

    async def exists(self, telegram_id: int) -> bool:
        return await super().exists(telegram_id=telegram_id)

    async def _clear_user_cache(self, telegram_id: int):
        await clear_cache(self.get, self, telegram_id)
        await clear_cache(self.get_with_group, self, telegram_id)
        await clear_cache(self.get_all, self)
