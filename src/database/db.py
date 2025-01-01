from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from database.models.base import Base
from utils.config import settings


class DatabaseHelperAlchemy:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_pre_ping: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_pre_ping=pool_pre_ping,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.sessionmaker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.sessionmaker() as session:
            yield session

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self.engine.dispose()

    async def delete_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    async def dispose(self):
        await self.engine.dispose()


db_helper = DatabaseHelperAlchemy(
    url=settings.db.url,
    echo=settings.db.echo,
    pool_pre_ping=settings.db.pre_ping,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow
)


def with_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        is_method = len(args) > 0 and hasattr(args[0], '__class__')
        async with db_helper.get_session() as session:
            if is_method:
                return await func(args[0], *args[1:], session=session, **kwargs)
            return await func(*args, session=session, **kwargs)
    return wrapper
