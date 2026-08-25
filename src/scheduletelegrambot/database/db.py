from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable


@dataclass(frozen=True, kw_only=True)
class EngineOptions:
    echo: bool = False
    echo_pool: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 5
    max_overflow: int = 10


class DatabaseAlchemy:
    def __init__(self, url: str, *, options: EngineOptions | None = None):
        options = options or EngineOptions()
        self._engine = create_async_engine(
            url=url,
            echo=options.echo,
            echo_pool=options.echo_pool,
            pool_pre_ping=options.pool_pre_ping,
            pool_size=options.pool_size,
            max_overflow=options.max_overflow,
        )
        self.sessionmaker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        async with self.sessionmaker() as session:
            yield session

    async def close(self) -> None:
        await self._engine.dispose()


def with_session(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "session" in kwargs:
            return await func(*args, **kwargs)

        if any(isinstance(arg, AsyncSession) for arg in args):
            return await func(*args, **kwargs)

        is_method = bool(args)
        db = cast(
            "DatabaseAlchemy | None",
            getattr(args[0], "db", None) if is_method else None,
        )

        if db is None:
            raise RuntimeError("Database dependency is not configured")

        async with db.get_session() as session:
            if is_method:
                return await func(args[0], *args[1:], session=session, **kwargs)
            return await func(*args, session=session, **kwargs)

    return wrapper
