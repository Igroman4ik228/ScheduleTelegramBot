from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.referrals import ReferralRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.schemas.referral import ReferralBaseSchema

_CACHE_TAG = "referrals"


class ReferralService:
    def __init__(self, referral_repository: ReferralRepository, uow: UoW) -> None:
        self.referral_repository = referral_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def list_all_by_owner(self, owner_id: int) -> list[ReferralBaseSchema]:
        models = await self.referral_repository.list_by_owner_id(owner_id)
        return [ReferralBaseSchema.model_validate(model) for model in models]

    async def create(self, owner_id: int, user_id: int) -> ReferralBaseSchema:
        model = await self.referral_repository.create(owner_id=owner_id, user_id=user_id)
        await self.uow.commit()
        await cache.delete_tags(_CACHE_TAG)

        return ReferralBaseSchema.model_validate(model)
