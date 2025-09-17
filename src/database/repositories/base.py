from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models.base import BaseModel
from utils.logger import LoggerMixin

TModel = TypeVar("Model", bound=BaseModel)


class BaseRepositoryAlchemy[TModel](LoggerMixin):
    def __init__(self, session: AsyncSession, model_cls: type[TModel]):
        self.session = session
        self.model_cls = model_cls

    async def create(self, **kwargs) -> TModel | None:
        instance = self.model_cls(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def get(self, *options: str, **kwargs) -> TModel | None:
        query = self._build_get_query(*options, limit=1, **kwargs)
        if query is None:
            return

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, *options: str, limit: int | None = None, **kwargs
    ) -> list[TModel]:
        query = self._build_get_query(*options, limit=limit, **kwargs)
        if query is None:
            return []

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def update(self, instance: TModel) -> TModel | None:
        instance_id = getattr(instance, "id", None)
        if instance_id is None:
            self.logger.warning(
                f"Instance {instance} must have an 'id' attribute for update."
            )
            return

        exist_instance = await BaseRepositoryAlchemy.get(self, id=instance_id)
        if exist_instance is None:
            self.logger.warning(
                f"Instance with id {instance_id} not exist for update"
            )
            return

        merged = await self.session.merge(instance)
        await self.session.commit()
        return merged

    async def delete(self, **kwargs):
        exist_instance = await BaseRepositoryAlchemy.get(self, **kwargs)
        if exist_instance is None:
            self.logger.warning(f"Instance with {kwargs} not exist for delete")
            return

        await self.session.delete(exist_instance)
        await self.session.commit()

    def _build_get_query(
        self, *options: str, limit: int | None = None, **filters
    ):
        for option in options:
            if not hasattr(self.model_cls, option):
                self.logger.warning(
                    f"Model {self.model_cls.__name__} has no attribute '{option}'"
                )
                return

        query = select(self.model_cls).filter_by(**filters).limit(limit)

        for option in options:
            query = query.options(joinedload(getattr(self.model_cls, option)))
        return query
