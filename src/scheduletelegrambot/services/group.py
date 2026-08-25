from __future__ import annotations

from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import GroupModel

if TYPE_CHECKING:
    from sqlalchemy.engine import CursorResult

    from scheduletelegrambot.database.repositories.groups import GroupRepository


class GroupService:
    def __init__(self, repository: GroupRepository) -> None:
        self.repository = repository

    async def get_by_id(self, group_id: int) -> GroupModel | None:
        return await self.repository.get_by_id(group_id)

    async def get_by_name(self, name: str) -> GroupModel | None:
        return await self.repository.get_one(GroupModel.name == name)

    async def get_all(self) -> list[GroupModel]:
        return await self.repository.get_many()

    async def get_all_by_department(self, department_id: int) -> list[GroupModel]:
        return await self.repository.get_many(GroupModel.department_id == department_id)

    async def get_all_by_global_shift(self, global_shift: int) -> list[GroupModel]:
        return await self.repository.get_many(GroupModel.global_shift == global_shift)

    async def delete_by_name(self, name: str) -> CursorResult[object]:
        return await self.repository.execute_delete(GroupModel.name == name)
