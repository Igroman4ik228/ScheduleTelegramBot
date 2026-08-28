from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.utils.logger import LoggerMixin


class UoW(LoggerMixin):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
            raise

    async def rollback(self) -> None:
        await self.session.rollback()
