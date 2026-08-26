from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import SubscribeModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class SubscribeRepository(BaseRepositoryAlchemy[SubscribeModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SubscribeModel)
