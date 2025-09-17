from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GroupModel
from database.repositories.base import BaseRepositoryAlchemy
from database.repositories.departments import DepartmentRepository


class GroupRepository(BaseRepositoryAlchemy[GroupModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, GroupModel)
        self.department_repo = DepartmentRepository(session)

    async def create(
        self, name: str, department_name: str
    ) -> GroupModel | None:
        department = await self.department_repo.get_by_name(department_name)
        if department is None:
            self.logger.debug(
                f"Department with name '{department_name}' not found"
            )
            return

        return await super().create(name=name, department_id=department.id)

    async def get(self, group_id: int, *options) -> GroupModel | None:
        return await super().get(id=group_id, *options)

    async def get_by_name(self, name: str, *options) -> GroupModel | None:
        return await super().get(name=name, *options)

    async def get_all_by_department(
        self, department_name: str
    ) -> list[GroupModel]:
        department = await self.department_repo.get_by_name(department_name)
        return await super().get_all(department_id=department.id)

    async def get_all_by_global_shift(
        self, global_shift: int
    ) -> list[GroupModel]:
        return await super().get_all(global_shift=global_shift)

    async def delete(self, group_id: int):
        await super().delete(id=group_id)

    async def delete_by_name(self, name: str):
        await super().delete(name=name)
