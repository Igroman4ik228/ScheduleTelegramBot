from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import ReferralModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class ReferralRepository(BaseRepositoryAlchemy[ReferralModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReferralModel)
