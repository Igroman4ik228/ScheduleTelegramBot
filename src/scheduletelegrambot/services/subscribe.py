from __future__ import annotations

from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import SubscribeModel

if TYPE_CHECKING:
    from scheduletelegrambot.database.repositories.subscribes import SubscribeRepository


class SubscribeService:
    def __init__(self, repository: SubscribeRepository) -> None:
        self.repository = repository

    async def get_by_id(self, subscribe_id: int) -> SubscribeModel | None:
        return await self.repository.get_by_id(subscribe_id)

    async def get_by_name(self, name: str) -> SubscribeModel | None:
        return await self.repository.get_one(SubscribeModel.name == name)

    async def get_all(self) -> list[SubscribeModel]:
        return await self.repository.get_many()

    async def get_all_by_price(self, price: int) -> list[SubscribeModel]:
        return await self.repository.get_many(SubscribeModel.price == price)
