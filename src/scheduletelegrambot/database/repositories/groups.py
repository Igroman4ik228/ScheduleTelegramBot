from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import GroupModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GroupRepository(BaseRepositoryAlchemy[GroupModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(self, session, GroupModel)

    async def get_by_name(self, name: str) -> GroupModel | None:
        return await self.get_one(GroupModel.name == name)

    async def get_all_by_department(self, department_id: int) -> list[GroupModel]:
        return await self.get_many(GroupModel.department_id == department_id)

    async def delete_by_name(self, name: str):
        await self._delete(GroupModel.name == name)
