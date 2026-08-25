from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import DefaultScheduleModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class DefaultScheduleRepository(BaseRepositoryAlchemy[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DefaultScheduleModel)
