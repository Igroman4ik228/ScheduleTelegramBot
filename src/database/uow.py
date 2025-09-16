import asyncio
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models.base import BaseModel
from database.repositories.users_copy import UserRepository


# todo: add auto commit
class UoW:
    _session: AsyncSession | None

    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        self._session_pool = session_pool
        self._session = None

    async def __aenter__(self) -> Self:
        self._session = await self._session_pool().__aenter__()
        self.users = UserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if self._session is None:
            return
        task: asyncio.Task[None] = asyncio.create_task(self._session.close())
        await asyncio.shield(task)
        self._session = None

    async def commit(self, *instances: BaseModel):
        self._session.add_all(instances)
        await self._session.commit()

    async def merge(self, *instances: BaseModel):
        for instance in instances:
            await self._session.merge(instance)

    async def delete(self, *instances: BaseModel):
        for instance in instances:
            await self._session.delete(instance)
        await self._session.commit()
