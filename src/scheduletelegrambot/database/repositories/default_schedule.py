from typing import TYPE_CHECKING

from cashews import NOT_NONE
from sqlalchemy import select

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.models import DefaultScheduleModel, GroupModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class DefaultScheduleRepository(BaseRepositoryAlchemy[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(self, session, DefaultScheduleModel)

    @cache.early(
        ttl="24h",
        early_ttl="12h",
        key=f"{CACHE_KEY_PREFIX}:default-schedule:{{weekday}}:{{shift}}:{{group_id}}",
        tags=("default-schedules",),
        condition=NOT_NONE,
    )
    async def get(self, weekday: int, shift: int, group_id: int) -> DefaultScheduleModel | None:
        return await self.get_one(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            DefaultScheduleModel.group_id == group_id,
        )

    @cache.early(
        ttl="24h",
        early_ttl="12h",
        key=f"{CACHE_KEY_PREFIX}:default-schedule:group-name:{{weekday}}:{{shift}}:{{group_name}}",
        tags=("default-schedules",),
        condition=NOT_NONE,
    )
    async def get_by_group_name(
        self, weekday: int, shift: int, group_name: str
    ) -> DefaultScheduleModel | None:
        return await self.get_one(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            DefaultScheduleModel.group.has(name=group_name),
        )

    async def create_by_group_name(
        self, weekday: int, shift: int, data_lessons: str, group_name: str
    ) -> DefaultScheduleModel | None:
        group = await self.session.scalar(select(GroupModel).where(GroupModel.name == group_name))
        if group is None:
            return None
        return await self.create(
            weekday=weekday,
            shift=shift,
            data_lessons=data_lessons,
            group_id=group.id,
        )

    async def create(self, **values: object) -> DefaultScheduleModel:
        instance = await super().create(**values)
        await self._invalidate()
        return instance

    async def update(self, instance: DefaultScheduleModel) -> DefaultScheduleModel:
        merged = await super().update(instance)
        await self._invalidate()
        return merged

    async def delete(self, instance: DefaultScheduleModel) -> None:
        await super().delete(instance)
        await self._invalidate()

    async def _invalidate(self) -> None:
        await invalidate_tags(self.session, "default-schedules")
