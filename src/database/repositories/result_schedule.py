from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.result_schedule import ResultScheduleModel
from database.redis.repositories import cached, clear_cache
from database.repositories.base import BaseRepositoryAlchemy
from database.repositories.groups import GroupRepository


class ResultScheduleRepository(BaseRepositoryAlchemy[ResultScheduleModel]):
    def __init__(self, session: AsyncSession):
        self.logger = getLogger(__name__)
        super().__init__(session, ResultScheduleModel)
        self.group_repo = GroupRepository(session)

    async def create(
        self,
        weekday: int,
        data_lessons: str,
        group_id: str
    ) -> ResultScheduleModel | None:
        return await super().create(weekday=weekday,
                                    data_lessons=data_lessons,
                                    group_id=group_id)

    async def create_by_group_name(
        self,
        weekday: int,
        data_lessons: str,
        group_name: str
    ) -> ResultScheduleModel | None:
        group = await self.group_repo.get_by_name(group_name)
        if group is None:
            self.logger.debug(f"Group {group_name} not found for create")
            return

        return await super().create(weekday=weekday,
                                    data_lessons=data_lessons,
                                    group_id=group.id)

    @cached(ttl=60*60*12)
    async def get(self, weekday: int, group_id: int, *options) -> ResultScheduleModel | None:
        return await super().get(weekday=weekday,
                                 group_id=group_id,
                                 *options)

    @cached(ttl=60*60*12)
    async def get_by_group_name(self, weekday: int, group_name: str, *options) -> ResultScheduleModel | None:
        group = await self.group_repo.get_by_name(group_name)
        if group is None:
            self.logger.debug(f"Group {group_name} not found for get")
            return

        return await super().get(weekday=weekday,
                                 group_id=group.id,
                                 *options)

    async def get_all(self, **kwargs):
        return await super().get_all(**kwargs)

    async def delete(self, weekday: int, group_id: int):
        await super().delete(weekday=weekday,
                             group_id=group_id)
        await self._clear_result_schedule_cache(weekday, group_id)

    async def delete_by_group_name(self, weekday: int, group_name: str):
        group = await self.group_repo.get_by_name(group_name)
        if group is None:
            self.logger.debug(f"Group {group_name} not found for delete")
            return

        await super().delete(weekday=weekday,
                             group_id=group.id)
        await self._clear_result_schedule_cache(weekday, group.id)

    async def _clear_result_schedule_cache(self, weekday: int, group_id: int):
        await clear_cache(self.get, self, weekday, group_id)
        await clear_cache(self.get_by_group_name, self)
