from sqlalchemy.ext.asyncio import AsyncSession

from database.models.subscribe import SubscribeModel
from database.repositories.base import BaseRepositoryAlchemy


class SubscribeRepository(BaseRepositoryAlchemy[SubscribeModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SubscribeModel)

    async def create(self,
                     name: str,
                     duration_days: int,
                     price: int,
                     **kwargs) -> SubscribeModel | None:
        return await super().create(name=name,
                                    duration_days=duration_days,
                                    price=price,
                                    **kwargs)

    async def get(self, subscribe_id: int, *options) -> SubscribeModel | None:
        return await super().get(id=subscribe_id, *options)

    async def get_by_name(self, name: str, *options) -> SubscribeModel | None:
        return await super().get(name=name, *options)

    async def delete(self, subscribe_id):
        await super().delete(id=subscribe_id)

    async def delete_by_name(self, name: str):
        await super().delete(name=name)
