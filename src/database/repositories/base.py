from logging import getLogger
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model
        self.logger = getLogger(__name__)

    async def create(self, **kwargs) -> T | None:
        exist_instance = await BaseRepository.get(self, **kwargs)
        if exist_instance is not None:
            self.logger.warning(
                f"Instance {repr(exist_instance)} "
                "already exist for create"
            )
            return

        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def get(self, **kwargs) -> T | None:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
        )
        return query.scalar_one_or_none()

    async def get_all(self, **kwargs) -> list[T]:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
        )
        return query.scalars().all()

    async def update(self, instance: T) -> T | None:
        exist_instance = await BaseRepository.get(self, id=instance.id)
        if exist_instance is None:
            self.logger.warning(
                f"Instance {repr(instance)} "
                "does not exist for update"
            )
            return

        for attr, value in instance.__dict__.items():
            if attr != '_sa_instance_state':
                setattr(instance, attr, value)

        self.session.add(instance)
        await self.session.commit()
        return instance

    async def delete(self, **kwargs) -> None:
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
