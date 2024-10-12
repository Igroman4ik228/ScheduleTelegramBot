from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.users import UserModel
from database.repositories.base import BaseRepository
from database.repositories.groups import GroupRepository


class UserRepository(BaseRepository[UserModel]):
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
        if group_name is not None:
            group = await self.group_repo.get(group_name)
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

    async def get(self, telegram_id: int) -> UserModel | None:
        return await super().get(telegram_id=telegram_id)

    async def get_with_group(self, telegram_id: int) -> UserModel | None:
        return await super().get_with_option("group", telegram_id=telegram_id)

    async def get_by_group(self, group_id: int) -> UserModel | None:
        return await super().get_all(group_id=group_id)

    async def get_by_premium(self, is_premium: bool) -> UserModel | None:
        return await super().get_all(is_premium=is_premium)

    async def delete(self, telegram_id: int):
        await super().delete(telegram_id=telegram_id)

    async def exists(self, telegram_id: int) -> bool:
        return await super().exists(telegram_id=telegram_id)
