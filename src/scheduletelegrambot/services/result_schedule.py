from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.result_schedule import ResultScheduleRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.schemas.result_schedule import (
    ResultScheduleBaseSchema,
    ResultScheduleWithGroupSchema,
)

_CACHE_TAG = "result-schedules"


class ResultScheduleService:
    def __init__(self, result_schedule_repository: ResultScheduleRepository, uow: UoW) -> None:
        self.result_schedule_repository = result_schedule_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="6h",
        early_ttl="4h",
        tags=(_CACHE_TAG, "result-schedule:{weekday}:{group_id}"),
        condition=NOT_NONE,
    )
    async def find(self, weekday: int, group_id: int) -> ResultScheduleBaseSchema | None:
        model = await self.result_schedule_repository.get_by_period_and_group(weekday, group_id)
        if not model:
            return None

        return ResultScheduleBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="6h",
        early_ttl="4h",
        tags=(_CACHE_TAG, "result-schedule:{weekday}:{group_id}"),
        condition=NOT_NONE,
    )
    async def find_with_group(
        self, weekday: int, group_id: int
    ) -> ResultScheduleWithGroupSchema | None:
        model = await self.result_schedule_repository.get_by_period_and_group_with_group(
            weekday, group_id
        )
        if not model:
            return None

        return ResultScheduleWithGroupSchema.model_validate(model)

    async def upsert_by_group_name(
        self, weekday: int, data_lessons: str, group_name: str
    ) -> ResultScheduleBaseSchema | None:
        model = await self.result_schedule_repository.create_or_update_by_group_name(
            weekday, data_lessons, group_name
        )

        if not model:
            return None

        await self.uow.commit()
        await cache.delete_tags(f"result-schedule:{weekday}:{model.group_id}")

        return ResultScheduleBaseSchema.model_validate(model)
