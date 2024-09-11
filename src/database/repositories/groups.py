from logging import getLogger

from sqlalchemy import delete, select, update

from database.db import sessionmaker
from database.models.groups import GroupModel
from database.repositories.departments import DepartmentRepository

logger = getLogger(__name__)


class GroupRepository:
    async def create(self, name: str, department_name: int) -> None:
        is_exist = await self._check_group_existence_by_name(name)
        if is_exist:
            logger.warning(f"Group with name '{name}' already exists")
            return

        department_rep = DepartmentRepository()
        department = await department_rep.get(department_name)
        if not department:
            logger.warning("Department with name "
                           f"'{department_name}' not found")
            return

        group = GroupModel(name=name, department_id=department.id)
        async with sessionmaker() as session:
            session.add(group)
            await session.commit()

    async def get_by_name(self, name: str) -> GroupModel | None:
        async with sessionmaker() as session:
            result_query = await session.execute(
                select(GroupModel)
                .filter_by(name=name)
            )
            return result_query.scalars().first()

    async def get_by_id(self, group_id: int) -> GroupModel | None:
        async with sessionmaker() as session:
            result_query = await session.execute(
                select(GroupModel)
                .filter_by(id=group_id)
            )
            return result_query.scalars().first()

    async def delete(self, group_id: int) -> None:
        is_exist = await self._check_group_existence_by_id(group_id)
        if not is_exist:
            logger.warning(f"Group '{group_id}' not found")
            return

        async with sessionmaker() as session:
            await session.execute(
                delete(GroupModel)
                .where(GroupModel.id == group_id)
            )
            await session.commit()

    async def update(self, group_id: int, new_name: str) -> None:
        is_exist = await self._check_group_existence_by_name(new_name)
        if is_exist:
            logger.warning(f"Group with name '{new_name}' already exists")
            return

        async with sessionmaker() as session:
            await session.execute(
                update(GroupModel)
                .where(GroupModel.id == group_id)
                .values(name=new_name)
            )
            await session.commit()

    async def _check_group_existence_by_name(self, name: str) -> bool:
        existing_group = await self.get_by_name(name)
        return existing_group is not None

    async def _check_group_existence_by_id(self, group_id: int) -> bool:
        existing_group = await self.get_by_id(group_id)
        return existing_group is not None
