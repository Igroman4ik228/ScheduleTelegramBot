from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import SubscribeModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class SubscribeRepository(BaseRepositoryAlchemy[SubscribeModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SubscribeModel)

    async def get_by_name(self, name: str) -> SubscribeModel | None:
        return await self.get_one(SubscribeModel.name == name)

    async def list_all(self) -> list[SubscribeModel]:
        return await self.get_many()

    async def list_by_price(self, price: int) -> list[SubscribeModel]:
        return await self.get_many(SubscribeModel.price == price)
