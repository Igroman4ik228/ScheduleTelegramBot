from __future__ import annotations

from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import ReferralModel

if TYPE_CHECKING:
    from scheduletelegrambot.database.repositories.referrals import ReferralRepository


class ReferralService:
    def __init__(self, repository: ReferralRepository) -> None:
        self.repository = repository

    async def get_all_by_owner(self, owner_id: int) -> list[ReferralModel]:
        return await self.repository.get_many(ReferralModel.owner_id == owner_id)

    async def create(self, owner_id: int, user_id: int) -> ReferralModel:
        return await self.repository.create(owner_id=owner_id, user_id=user_id)
