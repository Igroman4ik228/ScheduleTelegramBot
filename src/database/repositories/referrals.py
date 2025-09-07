from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ReferralModel
from database.repositories.base import BaseRepositoryAlchemy


class ReferralRepository(BaseRepositoryAlchemy):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ReferralModel)

    async def create(self, owner_id: int, user_id: int) -> ReferralModel | None:
        return await super().create(owner_id=owner_id, user_id=user_id)

    async def get(self, referral_id: int, *options) -> ReferralModel | None:
        return await super().get(id=referral_id, *options)

    async def get_by_user_id(
        self, user_id: int, *options
    ) -> ReferralModel | None:
        return await super().get(user_id=user_id, *options)

    async def delete(self, referral_id: int) -> None:
        await super().delete(id=referral_id)
