from logging import getLogger

from sqlalchemy import select

from database.db import sessionmaker
from database.models.default_schedule import DefaultScheduleModel
from database.repositories.groups import GroupRepository

logger = getLogger(__name__)


class DefaultScheduleRepository:
    async def create(self, shift: int, weekday: int, data_lessons: str, group_name: str) -> None:
        group_repo = GroupRepository()
        group = await group_repo.get_by_name(group_name)
        if not group:
            logger.warning(f"Group '{group_name}' not found")
            return

        default_schedule = DefaultScheduleModel(
            shift=shift,
            weekday=weekday,
            data_lessons=data_lessons,
            group_id=group.id
        )
        async with sessionmaker() as session:
            session.add(default_schedule)
            await session.commit()

    async def get(self, shift: int, weekday: int,):
        async with sessionmaker() as session:
            default_schedule_query = await session.execute(
                select(DefaultScheduleModel)
                .filter_by(shift=shift, weekday=weekday)
            )
        return default_schedule_query.scalar_one_or_none()

    async def delete(self, shift: int, weekday: int):
        default_schedule = self.get(shift, weekday)
        if not default_schedule:
            logger.warning("Default schedule on "
                           f"{weekday}({shift}) not found for delete")
            return

        async with sessionmaker() as session:
            await session.delete(default_schedule)
            await session.commit()
