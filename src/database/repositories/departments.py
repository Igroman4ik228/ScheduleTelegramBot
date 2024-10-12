from sqlalchemy.ext.asyncio import AsyncSession

from database.models.departments import DepartmentModel
from database.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[DepartmentModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DepartmentModel)

    async def create(self, name: str) -> DepartmentModel | None:
        return await super().create(name=name)

    async def get(self, name: str) -> DepartmentModel | None:
        return await super().get(name=name)

    async def delete(self, name: str):
        await super().delete(name=name)

    async def exists(self, name: str) -> bool:
        return await super().exists(name=name)
