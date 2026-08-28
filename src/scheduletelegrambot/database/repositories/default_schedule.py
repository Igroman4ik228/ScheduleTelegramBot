from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import DefaultScheduleModel, GroupModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class DefaultScheduleRepository(BaseRepositoryAlchemy[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DefaultScheduleModel)

    async def create_by_group_name(
        self, weekday: int, shift: int, data_lessons: str, group_name: str
    ) -> DefaultScheduleModel | None:
        group_id = await self.session.scalar(
            select(GroupModel.id).where(GroupModel.name == group_name)
        )
        if group_id is None:
            return None

        return await self.create(
            weekday=weekday,
            shift=shift,
            data_lessons=data_lessons,
            group_id=group_id,
        )

    async def get_by_period_and_group(
        self, weekday: int, shift: int, group_id: int
    ) -> DefaultScheduleModel | None:
        return await self.get_one(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            DefaultScheduleModel.group_id == group_id,
        )

    async def get_by_period_and_group_name(
        self, weekday: int, shift: int, group_name: str
    ) -> DefaultScheduleModel | None:
        return await self.get_one(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            DefaultScheduleModel.group.has(name=group_name),
        )

    async def list_by_group_and_shift(
        self, group_id: int, shift: int
    ) -> list[DefaultScheduleModel]:
        return await self.get_many(
            DefaultScheduleModel.group_id == group_id,
            DefaultScheduleModel.shift == shift,
        )

    async def list_by_period_with_group(
        self, weekday: int, shift: int
    ) -> list[DefaultScheduleModel]:
        return await self.get_many(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            options=(DefaultScheduleModel.group,),
        )

    async def execute_update_lessons(self, schedule_id: int, data_lessons: str) -> bool:
        result = await self.execute_update(
            DefaultScheduleModel.id == schedule_id,
            values={DefaultScheduleModel.data_lessons: data_lessons},
        )

        return result.rowcount > 0

    async def execute_delete_by_id(self, schedule_id: int) -> bool:
        result = await self.execute_delete(DefaultScheduleModel.id == schedule_id)

        return result.rowcount > 0
