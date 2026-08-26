from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import ResultScheduleModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)


class ResultScheduleRepository(BaseRepositoryAlchemy[ResultScheduleModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ResultScheduleModel)
