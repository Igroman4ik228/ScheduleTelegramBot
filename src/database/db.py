import asyncio

from sqlalchemy.ext.asyncio import (AsyncEngine, async_sessionmaker,
                                    create_async_engine)

from config import settings
from database.models.base import Base


async def create_tables(cur_engine: AsyncEngine) -> None:
    async with cur_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await cur_engine.dispose()


async def delete_tables(cur_engine: AsyncEngine) -> None:
    async with cur_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await cur_engine.dispose()


engine = create_async_engine(
    url=settings.database_url,
    echo=False,
    pool_pre_ping=True
)
sessionmaker = async_sessionmaker(engine,
                                  autoflush=False,
                                  expire_on_commit=False)

# Удаление таблиц
# asyncio.run(delete_tables(engine))


# Создание таблиц если их нет
asyncio.run(create_tables(engine))
