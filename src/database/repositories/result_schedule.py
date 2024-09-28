from logging import getLogger

from sqlalchemy import select

from database.db import sessionmaker
from database.models.result_schedule import ResultScheduleModel
from database.repositories.groups import GroupRepository

logger = getLogger(__name__)


class ResultScheduleRepository:
    def __init__(self):
        self.group_repo = GroupRepository()

    async def create(self, group_name: str, weekday: int, data_lessons: str) -> None:
        group = await self.group_repo.get_by_name(group_name)
        if not group:
            logger.warning(f"Group '{group_name}' not found")
            return

        result_schedule = ResultScheduleModel(
            weekday=weekday,
            data_lessons=data_lessons,
            group_id=group.id
        )
        async with sessionmaker() as session:
            session.add(result_schedule)
            await session.commit()

    async def get(self, group_name: str, weekday: int):
        group = await self.group_repo.get_by_name(group_name)
        if not group:
            logger.warning(f"Group '{group_name}' not found")
            return

        async with sessionmaker() as session:
            result_schedule_query = await session.execute(
                select(ResultScheduleModel)
                .filter_by(group_id=group.id)
                .filter_by(weekday=weekday)
            )
        return result_schedule_query.scalar_one_or_none()

    async def delete(self, group_name: str, weekday: int):
        result_schedule = await self.get(group_name, weekday)
        if not result_schedule:
            logger.warning("Result schedule on "
                           f"{weekday} not found for delete")
            return

        async with sessionmaker() as session:
            await session.delete(result_schedule)
            await session.commit()
