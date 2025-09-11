from logging import getLogger
from typing import TypeVar

from sqlalchemy import ColumnExpressionArgument, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models.base import BaseModel

Model = TypeVar("Model", bound=BaseModel)


class BaseRepositoryAlchemy[Model]:
    def __init__(self, session: AsyncSession, model: type[Model]):
        self.logger = getLogger(self.__class__.__name__)
        self.session = session
        self.type_model = model

    async def create(self, **kwargs) -> Model | None:
        instance = self.type_model(**kwargs)
        self.session.add(instance)
        return instance

    async def get(self, *options: str, **kwargs) -> Model | None:
        query = self._build_get_query(*options, limit=1, **kwargs)
        if query is None:
            return

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_where(
        self, *conditions: ColumnExpressionArgument[bool], **kwargs
    ) -> Model | None:
        return await self.session.scalar(
            select(self.type_model).where(*conditions)
        )

    async def get_all(
        self, *options: str, limit: int | None = None, **kwargs
    ) -> list[Model]:
        query = self._build_get_query(*options, limit=limit, **kwargs)
        if query is None:
            return []

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def update(self, instance: Model) -> Model | None:
        """Обновление"""
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
        await self.session.flush()
        return merged

    async def upsert(self, instance: Model) -> Model:
        """Обновление или вставка"""
        merged = await self.session.merge(instance)
        await self.session.flush()
        return merged

    async def delete(self, **kwargs):
        exist_instance = await BaseRepositoryAlchemy.get(self, **kwargs)
        if exist_instance is None:
            self.logger.warning(f"Instance with {kwargs} not exist for delete")
            return

        await self.session.delete(exist_instance)

    def _build_get_query(
        self, *options: str, limit: int | None = None, **filters
    ):
        for option in options:
            if not hasattr(self.type_model, option):
                self.logger.warning(
                    f"Model {self.type_model.__name__} has no attribute '{option}'"
                )
                return

        query = select(self.type_model).filter_by(**filters).limit(limit)

        for option in options:
            query = query.options(joinedload(getattr(self.type_model, option)))
        return query


class RepositoryException(Exception): ...
