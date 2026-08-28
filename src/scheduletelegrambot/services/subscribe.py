from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.subscribes import SubscribeRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.schemas.subscribe import SubscribeBaseSchema

_CACHE_TAG = "subscribes"


class SubscribeService:
    def __init__(self, subscribe_repository: SubscribeRepository, uow: UoW) -> None:
        self.subscribe_repository = subscribe_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_by_id(self, subscribe_id: int) -> SubscribeBaseSchema | None:
        model = await self.subscribe_repository.get_by_id(subscribe_id)
        if not model:
            return None

        return SubscribeBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_by_name(self, name: str) -> SubscribeBaseSchema | None:
        model = await self.subscribe_repository.get_by_name(name)
        if not model:
            return None

        return SubscribeBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
    )
    async def list_all(self) -> list[SubscribeBaseSchema]:
        models = await self.subscribe_repository.list_all()
        return [SubscribeBaseSchema.model_validate(model) for model in models]

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
    )
    async def list_all_by_price(self, price: int) -> list[SubscribeBaseSchema]:
        models = await self.subscribe_repository.list_by_price(price)
        return [SubscribeBaseSchema.model_validate(model) for model in models]
