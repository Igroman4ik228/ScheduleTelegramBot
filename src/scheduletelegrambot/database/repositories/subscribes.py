from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import SubscribeModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SubscribeRepository(BaseRepositoryAlchemy[SubscribeModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(self, session, SubscribeModel)

    async def get_by_name(self, name: str) -> SubscribeModel | None:
        return await self.get_one(SubscribeModel.name == name)

    async def get_many_by_price(self, price: int) -> list[SubscribeModel]:
        return await self.get_many(SubscribeModel.price == price)
