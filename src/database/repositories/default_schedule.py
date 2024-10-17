from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.default_schedule import DefaultScheduleModel
from database.repositories.base import BaseRepositoryAlchemy
from database.repositories.groups import GroupRepository


class DefaultScheduleRepository(BaseRepositoryAlchemy[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession):
        self.logger = getLogger(__name__)
        super().__init__(session, DefaultScheduleModel)
        self.group_repo = GroupRepository(session)

    async def create(
        self,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_id: str
    ) -> DefaultScheduleModel | None:
        return await super().create(weekday=weekday,
                                    shift=shift,
                                    data_lessons=data_lessons,
                                    group_id=group_id)

    async def create_by_group_name(
        self,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_name: str
    ) -> DefaultScheduleModel | None:
        group = await self.group_repo.get_by_name(group_name)
        if group is None:
            self.logger.debug(
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
        group_id: str
    ) -> DefaultScheduleModel | None:
        return await super().get(weekday=weekday,
                                 shift=shift,
                                 group_id=group_id)

    async def get_by_group_name(
        self,
        weekday: int,
        shift: int,
        group_name: str
    ) -> DefaultScheduleModel | None:
        group = await self.group_repo.get_by_name(group_name)
        if group is None:
            self.logger.debug(f"Group {group_name} not found for get")
            return

        return await super().get(weekday=weekday,
                                 shift=shift,
                                 group_id=group.id)

    async def delete(
        self,
        weekday: int,
        shift: int,
        group_id: str
    ):
        await super().delete(weekday=weekday,
                             shift=shift,
                             group_id=group_id)

    async def delete_by_group_name(
        self,
        weekday: int,
        shift: int,
        group_name: str
    ):
        group = await self.group_repo.get_by_name(group_name)
        if group is None:
            self.logger.debug(f"Group {group_name} not found for delete")
            return

        await super().delete(weekday=weekday,
                             shift=shift,
                             group_id=group.id)
