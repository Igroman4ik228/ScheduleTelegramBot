from logging import getLogger
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

T = TypeVar('T')


class BaseRepositoryAlchemy[T]:
    def __init__(self, session: AsyncSession, model: type[T]):
        self.logger = getLogger(__name__)
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T | None:
        instance = self.model(**kwargs)
        self.session.add(instance)
        if await self._handle_commit():
            return instance
        return

    async def get(self, **kwargs) -> T | None:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
        )
        return query.scalar_one_or_none()

    async def get_with_option(self, option: str, **kwargs) -> T | None:
        if not hasattr(self.model, option):
            self.logger.warning(
                f"Model {self.model.__name__}"
                f"has no attribute {option}"
            )
            return

        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
            .options(joinedload(getattr(self.model, option)))
        )
        return query.scalar_one_or_none()

    async def get_all(self, **kwargs) -> list[T]:
        query = await self.session.execute(
            select(self.model)
            .filter_by(**kwargs)
        )
        return query.scalars().all()

    async def update(self, instance: T):
        instance_id = getattr(instance, "id", None)
        is_exist = await BaseRepositoryAlchemy.exists(self, id=instance_id)
        if not is_exist:
            self.logger.debug(
                "Instance with id "
                f"{instance_id} not exist for update"
            )
            return

        await self.session.merge(instance)
        await self._handle_commit()

    async def delete(self, **kwargs):
        exist_instance = await BaseRepositoryAlchemy.get(self, **kwargs)
        if exist_instance is None:
            self.logger.debug(
                f"Instance with {kwargs} not exist for delete"
            )
            return

        await self.session.delete(exist_instance)
        await self._handle_commit()

    async def exists(self, **kwargs) -> bool:
        return await BaseRepositoryAlchemy.get(self, **kwargs) is not None

    async def _handle_commit(self) -> bool:
        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False
        except Exception as e:
            await self.session.rollback()
            raise f"Ошибка в репозиториях: {e}"
