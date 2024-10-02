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

    async def update(self, user: UserModel) -> None:
        await super().update(user)

    async def delete(self, telegram_id: int) -> None:
        await super().delete(telegram_id=telegram_id)

    async def exists(self, telegram_id: int) -> bool:
        return await super().exists(telegram_id=telegram_id)
