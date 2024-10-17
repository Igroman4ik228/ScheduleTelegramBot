from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.subscribe import SubscribeModel
from database.repositories.base import BaseRepositoryAlchemy


class SubscribeRepository(BaseRepositoryAlchemy[SubscribeModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SubscribeModel)

    async def create(self, name: str, duration: datetime, cost: int, **kwargs) -> SubscribeModel | None:
        return await super().create(name=name,
                                    duration=duration,
                                    cost=cost,
                                    **kwargs)

    async def get(self, subscribe_id: int) -> SubscribeModel | None:
        return await super().get(id=subscribe_id)

    async def get_by_name(self, name: str) -> SubscribeModel | None:
        return await super().get(name=name)

    async def delete(self, subscribe_id):
        await super().delete(id=subscribe_id)

    async def delete_by_name(self, name: str):
        await super().delete(name=name)
