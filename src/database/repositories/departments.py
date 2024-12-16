from sqlalchemy.ext.asyncio import AsyncSession

from database.models.departments import DepartmentModel
from database.repositories.base import BaseRepositoryAlchemy


class DepartmentRepository(BaseRepositoryAlchemy[DepartmentModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DepartmentModel)

    async def create(self, name: str) -> DepartmentModel | None:
        return await super().create(name=name)

    async def get(self, department_id: str, *options) -> DepartmentModel | None:
        return await super().get(id=department_id, *options)

    async def get_by_name(self, name: str, *options) -> DepartmentModel | None:
        return await super().get(name=name, *options)

    async def delete(self, name: str):
        await super().delete(name=name)
