from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GroupModel
from database.repositories.base_copy import BaseRepositoryAlchemy


class GroupRepository(BaseRepositoryAlchemy[GroupModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(session, GroupModel)

    async def get_by_name(self, name: str) -> GroupModel | None:
        return await self._get(GroupModel.name == name)

    async def get_many_by_department_name(
        self, department_id: int
    ) -> list[GroupModel]:
        return await self._get_many(GroupModel.department_id == department_id)

    async def delete_by_name(self, name: str):
        await self._delete(GroupModel.name == name)
