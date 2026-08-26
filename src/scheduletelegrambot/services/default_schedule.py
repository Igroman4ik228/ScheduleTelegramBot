from __future__ import annotations

from cashews import NOT_NONE

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache, invalidate_tags
from scheduletelegrambot.database.repositories.default_schedule import DefaultScheduleRepository
from scheduletelegrambot.schemas.default_schedule import (
    DefaultScheduleBaseSchema,
    DefaultScheduleCreateSchema,
    DefaultScheduleUpdateSchema,
    DefaultScheduleWithGroupSchema,
)


class DefaultScheduleService:
    def __init__(self, repository: DefaultScheduleRepository) -> None:
        self.repository = repository

    @cache.early(
        ttl="24h",
        early_ttl="12h",
        key=f"{CACHE_KEY_PREFIX}:default-schedule:{{weekday}}:{{shift}}:{{group_id}}",
        tags=("default-schedules",),
        condition=NOT_NONE,
    )
    async def find_for_group(
        self, weekday: int, shift: int, group_id: int
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.repository.get_by_period_and_group(weekday, shift, group_id)

        return DefaultScheduleBaseSchema.model_validate(model) if model else None

    @cache.early(
        ttl="24h",
        early_ttl="12h",
        key=f"{CACHE_KEY_PREFIX}:default-schedule:group-name:{{weekday}}:{{shift}}:{{group_name}}",
        tags=("default-schedules",),
        condition=NOT_NONE,
    )
    async def find_for_group_name(
        self, weekday: int, shift: int, group_name: str
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.repository.get_by_period_and_group_name(weekday, shift, group_name)

        return DefaultScheduleBaseSchema.model_validate(model) if model else None

    async def list_for_group(self, group_id: int, shift: int) -> list[DefaultScheduleBaseSchema]:
        models = await self.repository.list_by_group_and_shift(group_id, shift)

        return [DefaultScheduleBaseSchema.model_validate(model) for model in models]

    async def list_for_period(
        self, weekday: int, shift: int
    ) -> list[DefaultScheduleWithGroupSchema]:
        models = await self.repository.list_by_period_with_group(weekday, shift)

        return [DefaultScheduleWithGroupSchema.model_validate(model) for model in models]

    async def create_for_group(
        self, data: DefaultScheduleCreateSchema
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.repository.create_by_group_name(
            data.weekday, data.shift, data.data_lessons, data.group_name
        )

        await self._invalidate()

        return DefaultScheduleBaseSchema.model_validate(model) if model else None

    async def execute_update_lessons(self, data: DefaultScheduleUpdateSchema) -> bool:
        updated = await self.repository.execute_update_lessons(data.id, data.data_lessons)

        await self._invalidate()

        return updated

    async def _invalidate(self) -> None:
        await invalidate_tags(self.repository.session, "default-schedules")
