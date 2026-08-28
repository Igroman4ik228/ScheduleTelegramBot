from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.default_schedule import DefaultScheduleRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.schemas.default_schedule import (
    DefaultScheduleBaseSchema,
    DefaultScheduleCreateSchema,
    DefaultScheduleUpdateSchema,
    DefaultScheduleWithGroupSchema,
)

_CACHE_TAG = "default-schedules"


class DefaultScheduleService:
    def __init__(self, default_schedule_repository: DefaultScheduleRepository, uow: UoW) -> None:
        self.default_schedule_repository = default_schedule_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_for_group(
        self, weekday: int, shift: int, group_id: int
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.default_schedule_repository.get_by_period_and_group(
            weekday, shift, group_id
        )
        if not model:
            return None

        return DefaultScheduleBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_for_group_name(
        self, weekday: int, shift: int, group_name: str
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.default_schedule_repository.get_by_period_and_group_name(
            weekday, shift, group_name
        )
        if not model:
            return None

        return DefaultScheduleBaseSchema.model_validate(model)

    async def list_for_group(self, group_id: int, shift: int) -> list[DefaultScheduleBaseSchema]:
        models = await self.default_schedule_repository.list_by_group_and_shift(group_id, shift)

        return [DefaultScheduleBaseSchema.model_validate(model) for model in models]

    async def list_for_period(
        self, weekday: int, shift: int
    ) -> list[DefaultScheduleWithGroupSchema]:
        models = await self.default_schedule_repository.list_by_period_with_group(weekday, shift)

        return [DefaultScheduleWithGroupSchema.model_validate(model) for model in models]

    async def create_for_group(
        self, data: DefaultScheduleCreateSchema
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.default_schedule_repository.create_by_group_name(
            data.weekday, data.shift, data.data_lessons, data.group_name
        )

        if not model:
            return None

        await self.uow.commit()
        await cache.delete_tags(_CACHE_TAG)

        return DefaultScheduleBaseSchema.model_validate(model)

    async def update_lessons(self, data: DefaultScheduleUpdateSchema) -> bool:
        updated = await self.default_schedule_repository.execute_update_lessons(
            data.id, data.data_lessons
        )

        if updated:
            await self.uow.commit()
            await cache.delete_tags(_CACHE_TAG)

        return updated
