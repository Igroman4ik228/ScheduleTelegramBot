from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import DepartmentModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class DepartmentRepository(BaseRepositoryAlchemy[DepartmentModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(self, session, DepartmentModel)

    async def get_by_name(self, name: str) -> DepartmentModel | None:
        return await self.get_one(DepartmentModel.name == name)
