from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DefaultScheduleModel
from database.repositories.base_copy import BaseRepositoryAlchemy


class DefaultScheduleRepository(BaseRepositoryAlchemy[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(session, DefaultScheduleModel)

    async def get(
        self, weekday: int, shift: int, group_id: int
    ) -> DefaultScheduleModel | None:
        return await self._get(
            DefaultScheduleModel.weekday == weekday,
            DefaultScheduleModel.shift == shift,
            DefaultScheduleModel.group_id == group_id,
        )
