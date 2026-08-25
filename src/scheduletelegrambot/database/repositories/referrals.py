from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import ReferralModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ReferralRepository(BaseRepositoryAlchemy[ReferralModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReferralModel)

    async def get_all_by_owner(self, owner_id: int) -> list[ReferralModel]:
        return await self.get_many(ReferralModel.owner_id == owner_id)
