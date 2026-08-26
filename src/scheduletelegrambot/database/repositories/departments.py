from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import DepartmentModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class DepartmentRepository(BaseRepositoryAlchemy[DepartmentModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DepartmentModel)
