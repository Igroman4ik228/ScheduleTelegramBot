from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import GroupModel, ResultScheduleModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)
from scheduletelegrambot.enums import Weekday


class ResultScheduleRepository(BaseRepositoryAlchemy[ResultScheduleModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ResultScheduleModel)

    async def get_by_period_and_group(
        self, weekday: Weekday, group_id: int
    ) -> ResultScheduleModel | None:
        return await self.get_one(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
        )

    async def get_by_period_and_group_with_group(
        self, weekday: Weekday, group_id: int
    ) -> ResultScheduleModel | None:
        return await self.get_one(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
            options=(ResultScheduleModel.group,),
        )

    async def create_or_update_by_group_name(
        self, weekday: Weekday, data_lessons: str, group_name: str
    ) -> ResultScheduleModel | None:
        group_id = await self._session.scalar(
            select(GroupModel.id).where(GroupModel.name == group_name)
        )
        if group_id is None:
            return None

        instance = await self.get_by_period_and_group(weekday, group_id)
        if instance is None:
            return await self.create(
                weekday=weekday,
                data_lessons=data_lessons,
                group_id=group_id,
            )

        instance.data_lessons = data_lessons
        return await self.update(instance)
