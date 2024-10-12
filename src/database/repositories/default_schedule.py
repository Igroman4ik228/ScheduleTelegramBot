from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.default_schedule import DefaultScheduleModel
from database.repositories.base import BaseRepository
from database.repositories.groups import GroupRepository


class DefaultScheduleRepository(BaseRepository[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession):
        self.logger = getLogger(__name__)
        super().__init__(session, DefaultScheduleModel)
        self.group_repo = GroupRepository(session)

    async def create(
        self,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_name: str
    ) -> DefaultScheduleModel | None:
        group = await self.group_repo.get(group_name)
        if group is None:
            self.logger.warning(
                f"Group {group_name} not found for create"
            )
            return

        return await super().create(weekday=weekday,
                                    shift=shift,
                                    data_lessons=data_lessons,
                                    group_id=group.id)

    async def get(
        self,
        weekday: int,
        shift: int,
        group_name: str
    ) -> DefaultScheduleModel | None:
        group = await self.group_repo.get(group_name)
        if group is None:
            self.logger.warning(f"Group {group_name} not found for get")
            return

        return await super().get(weekday=weekday,
                                 shift=shift,
                                 group_id=group.id)

    async def delete(
        self,
        weekday: int,
        shift: int,
        group_name: str
    ):
        group = await self.group_repo.get(group_name)
        if group is None:
            self.logger.warning(f"Group {group_name} not found for delete")
            return

        await super().delete(group_name=group_name,
                             weekday=weekday,
                             shift=shift)

    async def exists(
        self,
        group_name: str,
        weekday: int,
        shift: int
    ) -> bool:
        group = await self.group_repo.get(group_name)
        if group is None:
            self.logger.warning(f"Group {group_name} not found for exists")
            return

        return await super().exists(group.id,
                                    weekday,
                                    shift)
