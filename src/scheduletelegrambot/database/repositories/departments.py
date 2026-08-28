from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import DepartmentModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class DepartmentRepository(BaseRepositoryAlchemy[DepartmentModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DepartmentModel)

    async def get_by_name(self, name: str) -> DepartmentModel | None:
        return await self.get_one(DepartmentModel.name == name)

    async def list_all(self) -> list[DepartmentModel]:
        return await self.get_many()
