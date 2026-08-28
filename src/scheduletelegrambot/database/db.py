from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)


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

    async def close(self) -> None:
        await self._engine.dispose()
