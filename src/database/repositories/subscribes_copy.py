from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SubscribeModel
from database.repositories.base_copy import BaseRepositoryAlchemy


class SubscribeRepository(BaseRepositoryAlchemy[SubscribeModel]):
    def __init__(self, session: AsyncSession):
        BaseRepositoryAlchemy.__init__(self, session, SubscribeModel)

    async def get_by_name(self, name: str) -> SubscribeModel | None:
        return await self._get(SubscribeModel.name == name)

    async def get_many_by_price(self, price: int) -> list[SubscribeModel]:
        return await self._get_many(SubscribeModel.price == price)
