from __future__ import annotations

from typing import TYPE_CHECKING

from cashews import NOT_NONE

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.models import GroupModel, ResultScheduleModel

if TYPE_CHECKING:
    from scheduletelegrambot.database.repositories.groups import GroupRepository
    from scheduletelegrambot.database.repositories.result_schedule import ResultScheduleRepository


class ResultScheduleService:
    def __init__(
        self, repository: ResultScheduleRepository, group_repository: GroupRepository
    ) -> None:
        self.repository = repository
        self.group_repository = group_repository

    @cache.early(
        ttl="6h",
        early_ttl="4h",
        key=f"{CACHE_KEY_PREFIX}:result-schedule:{{weekday}}:{{group_id}}",
        tags=("result-schedules", "result-schedule:{weekday}:{group_id}"),
        condition=NOT_NONE,
    )
    async def get(self, weekday: int, group_id: int) -> ResultScheduleModel | None:
        return await self.repository.get_one(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
        )

    @cache.early(
        ttl="6h",
        early_ttl="4h",
        key=f"{CACHE_KEY_PREFIX}:result-schedule:{{weekday}}:{{group_id}}:group",
        tags=("result-schedules", "result-schedule:{weekday}:{group_id}"),
        condition=NOT_NONE,
    )
    async def get_with_group(self, weekday: int, group_id: int) -> ResultScheduleModel | None:
        return await self.repository.get_one(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
            options=(ResultScheduleModel.group,),
        )

    async def upsert_by_group_name(
        self, weekday: int, data_lessons: str, group_name: str
    ) -> ResultScheduleModel | None:
        group = await self.group_repository.get_one(GroupModel.name == group_name)
        if group is None:
            return None

        instance = await self.get(weekday, group.id)
        if instance is None:
            instance = await self.repository.create(
                weekday=weekday,
                data_lessons=data_lessons,
                group_id=group.id,
            )
        else:
            instance.data_lessons = data_lessons
            instance = await self.repository.update(instance)

        await self._invalidate(instance.weekday, instance.group_id)
        return instance

    async def _invalidate(self, weekday: int, group_id: int) -> None:
        await invalidate_tags(self.repository.session, f"result-schedule:{weekday}:{group_id}")
