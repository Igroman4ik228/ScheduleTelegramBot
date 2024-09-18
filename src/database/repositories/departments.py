from logging import getLogger

from sqlalchemy import delete, select

from database.db import sessionmaker
from database.models.departments import DepartmentModel

logger = getLogger(__name__)


class DepartmentRepository:
    async def create(self, name: str) -> None:
        department = DepartmentModel(
            name=name
        )
        async with sessionmaker() as session:
            session.add(department)
            await session.commit()

    async def get(self, name: str) -> DepartmentModel | None:
        async with sessionmaker() as session:
            result_query = await session.execute(
                select(DepartmentModel)
                .filter_by(name=name)
            )
            return result_query.scalar_one_or_none()

    async def delete(self, name: str) -> None:
        department = await self.get(name)
        if not department:
            logger.warning(f"Department '{name}' not found")
            return

        async with sessionmaker() as session:
            await session.execute(
                delete(DepartmentModel)
                .where(DepartmentModel.name == name)
            )
            await session.commit()
