from logging import getLogger

from sqlalchemy import select

from database.db import sessionmaker
from database.models.result_schedule import ResultScheduleModel
from database.repositories.groups import GroupRepository

logger = getLogger(__name__)


class ResultScheduleRepository:
    async def create(self, weekday: int, data_lessons: str, group_name: str) -> None:
        group_repo = GroupRepository()
        group = await group_repo.get_by_name(group_name)
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

    async def get(self, weekday: int):
        async with sessionmaker() as session:
            user_query = await session.execute(
                select(ResultScheduleModel)
                .filter_by(weekday=weekday)
            )
        return user_query.scalars().first()

    async def delete(self, weekday: int):
        result_schedule = self.get(weekday)
        if not result_schedule:
            logger.warning("Result schedule on "
                           f"{weekday} not found for delete")
            return

        async with sessionmaker() as session:
            await session.delete(result_schedule)
            await session.commit()
