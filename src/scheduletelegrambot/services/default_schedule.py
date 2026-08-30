from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.default_schedule import DefaultScheduleRepository
from scheduletelegrambot.enums import StudyShift, Weekday, WeekType
from scheduletelegrambot.schemas.default_schedule import (
    DefaultScheduleBaseSchema,
    DefaultScheduleWithGroupSchema,
)

_CACHE_TAG = "default-schedules"


class DefaultScheduleService:
    def __init__(self, default_schedule_repository: DefaultScheduleRepository) -> None:
        self.default_schedule_repository = default_schedule_repository

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_for_group(
        self, weekday: Weekday, week_type: WeekType, group_id: int
    ) -> DefaultScheduleBaseSchema | None:
        model = await self.default_schedule_repository.get_by_period_and_group(
            weekday, week_type, group_id
        )
        return DefaultScheduleBaseSchema.model_validate(model) if model else None

    async def list_for_group(
        self, group_id: int, week_type: WeekType
    ) -> list[DefaultScheduleBaseSchema]:
        models = await self.default_schedule_repository.list_by_group_and_week_type(
            group_id, week_type
        )
        return [DefaultScheduleBaseSchema.model_validate(model) for model in models]

    async def list_for_period_and_study_shift(
        self, weekday: Weekday, week_type: WeekType, study_shift: StudyShift
    ) -> list[DefaultScheduleWithGroupSchema]:
        models = await self.default_schedule_repository.list_by_period_and_study_shift_with_group(
            weekday, week_type, study_shift
        )
        return [DefaultScheduleWithGroupSchema.model_validate(model) for model in models]
