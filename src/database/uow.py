from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models.base import BaseModel
from database.repository import CachedRepository, Repository
from helpers.cache import CacheHelper
from utils.logger import LoggerMixin


class UoW(LoggerMixin):
    """
    example:
        async with UoW(sessionmaker) as (uow,rep):...
    """

    def __init__(
        self,
        session_pool: async_sessionmaker[AsyncSession],
        commit: bool = False,
    ):
        self._session_pool = session_pool
        self._commit = commit
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = await self._session_pool().__aenter__()
        self.rep = Repository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if self._session is None:
            return
        try:
            if self._commit and exc_type is None:
                await self._session.commit()
        except Exception as e:
            self.logger.error(f"Exception on commit: {e}", exc_info=True)
            await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self, *instances: BaseModel):
        if self._session is None:
            raise RuntimeError("Session is not initialized.")
        self._session.add_all(instances)
        await self._session.commit()

    async def merge(self, *instances: BaseModel):
        if self._session is None:
            raise RuntimeError("Session is not initialized.")
        for instance in instances:
            await self._session.merge(instance)

    async def delete(self, *instances: BaseModel):
        if self._session is None:
            raise RuntimeError("Session is not initialized.")
        for instance in instances:
            await self._session.delete(instance)
        await self._session.commit()


class CachedUoW(UoW):
    """
    example:
        async with CachedUoW(sessionmaker, cache_helper) as (uow,rep):...
    """

    def __init__(
        self,
        session_pool: async_sessionmaker[AsyncSession],
        cache_helper: CacheHelper,
        commit: bool = False,
    ):
        super().__init__(session_pool, commit)
        self._cache_helper = cache_helper

    async def __aenter__(self) -> Self:
        self._session = await self._session_pool().__aenter__()
        self.rep = CachedRepository(self._session, self._cache_helper)
        return self
