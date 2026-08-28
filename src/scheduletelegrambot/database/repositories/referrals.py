from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import ReferralModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class ReferralRepository(BaseRepositoryAlchemy[ReferralModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReferralModel)

    async def list_by_owner_id(self, owner_id: int) -> list[ReferralModel]:
        return await self.get_many(ReferralModel.owner_id == owner_id)
