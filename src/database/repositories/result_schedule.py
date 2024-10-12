from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.result_schedule import ResultScheduleModel
from database.repositories.base import BaseRepository
from database.repositories.groups import GroupRepository

logger = getLogger(__name__)


class ResultScheduleRepository(BaseRepository[ResultScheduleModel]):
    def __init__(self, session: AsyncSession):
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
        group = await self.group_repo.get(group_name)
        if group is None:
            logger.warning(f"Group {group_name} not found for create")
            return

        return await super().create(weekday=weekday,
                                    data_lessons=data_lessons,
                                    group_id=group.id)

    async def get(
            self,
            weekday: int,
            group_id: str
    ) -> ResultScheduleModel | None:
        return await super().get(weekday=weekday,
                                 group_id=group_id)

    async def get_by_group_name(
            self,
            weekday: int,
            group_name: str
    ) -> ResultScheduleModel | None:
        group = await self.group_repo.get(group_name)
        if group is None:
            logger.warning(f"Group {group_name} not found for get")
            return

        return await super().get(weekday=weekday,
                                 group_id=group.id)

    async def delete(
            self,
            weekday: int,
            group_id: str):
        await super().delete(weekday=weekday,
                             group_id=group_id)

    async def delete_by_group_name(
            self,
            weekday: int,
            group_name: str):
        group = await self.group_repo.get(group_name)
        if group is None:
            logger.warning(f"Group {group_name} not found for delete")
            return

        await super().delete(weekday=weekday,
                             group_id=group.id)

    async def exists(self,
                     weekday: int,
                     group_name: str) -> bool:
        group = await self.group_repo.get(group_name)
        if group is None:
            logger.warning(f"Group {group_name} not found for create")
            return

        return await super().exists(weekday=weekday,
                                    group_id=group.id)
