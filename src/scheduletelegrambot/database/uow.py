from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.utils.logger import LoggerMixin


class UoW(LoggerMixin):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except:
            await self._session.rollback()
            raise

    async def rollback(self) -> None:
        await self._session.rollback()

    def begin(self):
        return self._session.begin()

    async def refresh(self, instance: object) -> None:
        await self._session.refresh(instance)
