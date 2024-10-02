from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.groups import GroupModel
from database.repositories.base import BaseRepository
from database.repositories.departments import DepartmentRepository


class GroupRepository(BaseRepository[GroupModel]):
    def __init__(self, session: AsyncSession):
        self.logger = getLogger(__name__)
        super().__init__(session, GroupModel)
        self.department_repo = DepartmentRepository(session)

    async def create(
            self,
            name: str,
            department_name: str
    ) -> GroupModel | None:
        department = await self.department_repo.get(department_name)
        if department is None:
            self.logger.warning("Department with name "
                                f"'{department_name}' not found")
            return

        return await super().create(name=name,
                                    department_id=department.id)

    async def get(self, name: str) -> GroupModel | None:
        return await super().get(name=name)

    async def update(self, group: GroupModel) -> GroupModel | None:
        return await super().update(group)

    async def delete(self, name: str) -> None:
        await super().delete(name=name)
