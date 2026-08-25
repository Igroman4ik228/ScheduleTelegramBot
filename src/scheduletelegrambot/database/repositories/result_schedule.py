from typing import TYPE_CHECKING

from cashews import NOT_NONE
from sqlalchemy import select

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.models import GroupModel, ResultScheduleModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ResultScheduleRepository(BaseRepositoryAlchemy[ResultScheduleModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ResultScheduleModel)

    @cache.early(
        ttl="6h",
        early_ttl="4h",
        key=f"{CACHE_KEY_PREFIX}:result-schedule:{{weekday}}:{{group_id}}",
        tags=("result-schedule:{weekday}:{group_id}",),
        condition=NOT_NONE,
    )
    async def get(self, weekday: int, group_id: int) -> ResultScheduleModel | None:
        return await self.get_one(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
        )

    @cache.early(
        ttl="6h",
        early_ttl="4h",
        key=f"{CACHE_KEY_PREFIX}:result-schedule:{{weekday}}:{{group_id}}:group",
        tags=("result-schedule:{weekday}:{group_id}",),
        condition=NOT_NONE,
    )
    async def get_with_group(self, weekday: int, group_id: int) -> ResultScheduleModel | None:
        return await self.get_one(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
            options=(ResultScheduleModel.group,),
        )

    async def update(self, instance: ResultScheduleModel) -> ResultScheduleModel:
        merged = await super().update(instance)

        await self._invalidate(instance.weekday, instance.group_id)

        return merged

    async def create(self, **values: object) -> ResultScheduleModel:
        instance = await super().create(**values)

        await self._invalidate(instance.weekday, instance.group_id)

        return instance

    async def delete(self, instance: ResultScheduleModel) -> None:
        await super().delete(instance)

        await self._invalidate(instance.weekday, instance.group_id)

    async def upsert_by_group_name(
        self, weekday: int, data_lessons: str, group_name: str
    ) -> ResultScheduleModel | None:
        group = await self._get_group_by_name(group_name)
        if group is None:
            return None

        result = await self.get(weekday, group.id)
        if result is None:
            return await self.create(
                weekday=weekday,
                data_lessons=data_lessons,
                group_id=group.id,
            )

        result.data_lessons = data_lessons
        return await self.update(result)

    async def _get_group_by_name(self, group_name: str):
        return await self.session.scalar(select(GroupModel).where(GroupModel.name == group_name))

    async def _invalidate(self, weekday: int, group_id: int) -> None:
        await invalidate_tags(self.session, f"result-schedule:{weekday}:{group_id}")
