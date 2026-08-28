from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import GroupModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)


class GroupRepository(BaseRepositoryAlchemy[GroupModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GroupModel)

    async def get_by_name(self, name: str) -> GroupModel | None:
        return await self.get_one(GroupModel.name == name)

    async def list_all(self) -> list[GroupModel]:
        return await self.get_many()

    async def list_by_department(self, department_id: int) -> list[GroupModel]:
        return await self.get_many(GroupModel.department_id == department_id)

    async def list_by_global_shift(self, global_shift: int) -> list[GroupModel]:
        return await self.get_many(GroupModel.global_shift == global_shift)

    async def execute_delete_by_name(self, name: str) -> CursorResult[object]:
        return await self.execute_delete(GroupModel.name == name)
