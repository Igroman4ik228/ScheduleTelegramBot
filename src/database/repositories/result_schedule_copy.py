from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ResultScheduleModel
from database.repositories.base_copy import BaseRepositoryAlchemy
from helpers.cache import (
    Cacheable,
    CacheHelper,
    cached,
    clear_cache,
)
from utils.constants import CacheTTL


class ResultScheduleRepository(
    BaseRepositoryAlchemy[ResultScheduleModel], Cacheable
):
    def __init__(
        self,
        session: AsyncSession,
        cache_helper: CacheHelper,
    ):
        BaseRepositoryAlchemy.__init__(self, session, ResultScheduleModel)
        Cacheable.__init__(self, cache_helper)

    @cached(ttl_seconds=CacheTTL.RESULT_SCHEDULE.value)
    async def get(
        self, weekday: int, group_id: int
    ) -> ResultScheduleModel | None:
        return await self._get(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
        )

    @cached(ttl_seconds=CacheTTL.RESULT_SCHEDULE.value)
    async def get_with_group(
        self, weekday: int, group_id: int
    ) -> ResultScheduleModel | None:
        return await self._get(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
            options=(ResultScheduleModel.group,),
        )

    async def update(
        self, instance: ResultScheduleModel
    ) -> ResultScheduleModel:
        await self._clear_result_schedule_cache(
            instance.weekday, instance.group_id
        )

        return await self.session.merge(instance)

    async def delete(self, instance: ResultScheduleModel):
        await self._clear_result_schedule_cache(
            instance.weekday, instance.group_id
        )

        await self.session.delete(instance)

    async def delete_by(self, weekday: int, group_id: int):
        await self._clear_result_schedule_cache(weekday, group_id)

        await self._delete(
            ResultScheduleModel.weekday == weekday,
            ResultScheduleModel.group_id == group_id,
        )

    async def _clear_result_schedule_cache(self, weekday: int, group_id: int):
        await clear_cache(self.get, self, weekday, group_id)
        await clear_cache(self.get_with_group, self, weekday, group_id)
