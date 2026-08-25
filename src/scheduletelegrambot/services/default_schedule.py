from __future__ import annotations

from typing import TYPE_CHECKING

from cashews import NOT_NONE

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.models import DefaultScheduleModel, GroupModel

if TYPE_CHECKING:
    from scheduletelegrambot.database.repositories.default_schedule import DefaultScheduleRepository
    from scheduletelegrambot.database.repositories.groups import GroupRepository


class DefaultScheduleService:
    def __init__(
        self, repository: DefaultScheduleRepository, group_repository: GroupRepository
    ) -> None:
        self.repository = repository
        self.group_repository = group_repository

    @cache.early(
        ttl="24h",
        early_ttl="12h",
        key=f"{CACHE_KEY_PREFIX}:default-schedule:{{weekday}}:{{shift}}:{{group_id}}",
        tags=("default-schedules",),
        condition=NOT_NONE,
    )
    async def get(self, weekday: int, shift: int, group_id: int) -> DefaultScheduleModel | None:
        return await self.repository.get_one(
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
        return await self.repository.get_one(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            DefaultScheduleModel.group.has(name=group_name),
        )

    async def get_all_by_group_and_shift(
        self, group_id: int, shift: int
    ) -> list[DefaultScheduleModel]:
        return await self.repository.get_many(
            DefaultScheduleModel.group_id == group_id,
            DefaultScheduleModel.shift == shift,
        )

    async def get_all_by_weekday_and_shift_with_group(
        self, weekday: int, shift: int
    ) -> list[DefaultScheduleModel]:
        return await self.repository.get_many(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            options=(DefaultScheduleModel.group,),
        )

    async def create_by_group_name(
        self, weekday: int, shift: int, data_lessons: str, group_name: str
    ) -> DefaultScheduleModel | None:
        group = await self.group_repository.get_one(GroupModel.name == group_name)
        if group is None:
            return None

        instance = await self.repository.create(
            weekday=weekday,
            shift=shift,
            data_lessons=data_lessons,
            group_id=group.id,
        )
        await self._invalidate()
        return instance

    async def update_lessons(
        self, schedule: DefaultScheduleModel, data_lessons: str
    ) -> DefaultScheduleModel:
        schedule.data_lessons = data_lessons
        updated = await self.repository.update(schedule)
        await self._invalidate()
        return updated

    async def _invalidate(self) -> None:
        await invalidate_tags(self.repository.session, "default-schedules")
