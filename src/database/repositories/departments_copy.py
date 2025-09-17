from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DepartmentModel
from database.repositories.base_copy import BaseRepositoryAlchemy


class DepartmentRepository(BaseRepositoryAlchemy[DepartmentModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(self, session, DepartmentModel)

    async def get_by_name(self, name: str) -> DepartmentModel | None:
        return await self._get(DepartmentModel.name == name)
