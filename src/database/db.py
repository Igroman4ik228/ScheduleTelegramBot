from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseAlchemy:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_pre_ping: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self._engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_pre_ping=pool_pre_ping,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.sessionmaker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.sessionmaker() as session:
            yield session

    async def close(self):
        await self._engine.dispose()


# todo: refactor to with_uow
def with_session(func):
    """
    Декоратор для автоматического управления сессией.
    Если сессия уже передана — использует её.
    Если это метод класса — ищет self.db.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "session" in kwargs:
            return await func(*args, **kwargs)

        if any(isinstance(arg, AsyncSession) for arg in args):
            return await func(*args, **kwargs)

        is_method = args and hasattr(args[0], "__class__")

        if is_method:
            db: DatabaseAlchemy = getattr(args[0], "db", None)

        if db is None:
            raise RuntimeError(
                "DB не найден. Передайте session или self.db должен быть определен."
            )

        async with db.get_session() as session:
            if is_method:
                return await func(args[0], *args[1:], session=session, **kwargs)
            return await func(*args, session=session, **kwargs)

    return wrapper
