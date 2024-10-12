from logging import getLogger
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

T = TypeVar('T')


class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model: type[T]):
        self.logger = getLogger(__name__)
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T | None:
        instance = self.model(**kwargs)
        self.session.add(instance)
        try:
            await self.session.commit()
            return instance
        except IntegrityError:
            self.logger.debug(
                f"Instance {repr(instance)} "
                "already exist for create"
            )
            await self.session.rollback()
            return None

    async def get(self, **kwargs) -> T | None:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
        )
        return query.scalar_one_or_none()

    async def get_with_option(self, option: str, **kwargs) -> T | None:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
            .options(joinedload(self.model.__dict__[option]))
        )
        return query.scalar_one_or_none()

    async def get_all(self, **kwargs) -> list[T]:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
        )
        return query.scalars().all()

    async def update(self, instance: T):
        # Создаёт новую запись если не существует
        await self.session.merge(instance)
        await self.session.commit()

    async def delete(self, **kwargs):
        exist_instance = await BaseRepository.get(self, **kwargs)
        if exist_instance is None:
            self.logger.warning(
                f"Instance with {kwargs} not exist for delete"
            )
            return

        await self.session.delete(exist_instance)
        await self.session.commit()

    async def exists(self, **kwargs) -> bool:
        return bool(await BaseRepository.get(self, **kwargs))
