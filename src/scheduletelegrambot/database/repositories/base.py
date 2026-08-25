from typing import TYPE_CHECKING, Any, final

from sqlalchemy import ColumnExpressionArgument, delete, inspect, select
from sqlalchemy.orm import QueryableAttribute, joinedload, selectinload
from sqlalchemy.sql.functions import count

from scheduletelegrambot.database.models.base import BaseModel
from scheduletelegrambot.utils.logger import LoggerMixin

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_LIMIT = 10_000


class BaseRepositoryAlchemy[TModel: BaseModel](LoggerMixin):
    def __init__(self, session: AsyncSession, model_cls: type[TModel]) -> None:
        self.session = session
        self.model_cls = model_cls

    async def create(self, **values: Any) -> TModel:
        instance = self.model_cls(**values)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, object_id: int) -> TModel | None:
        return self._detach(await self.session.get(self.model_cls, object_id))

    async def update(self, instance: TModel) -> TModel:
        merged = await self.session.merge(instance)
        await self.session.flush()
        return merged

    async def delete(self, instance: TModel) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def get_one(
        self,
        *conditions: ColumnExpressionArgument[bool],
        options: tuple[QueryableAttribute[Any], ...] = (),
    ) -> TModel | None:
        query = self._build_get_query(*conditions, limit=1)
        for option in options:
            query = query.options(joinedload(option))
        return self._detach(await self.session.scalar(query))

    async def get_many(
        self,
        *conditions: ColumnExpressionArgument[bool],
        options: tuple[QueryableAttribute[Any], ...] = (),
        limit: int | None = DEFAULT_LIMIT,
    ) -> list[TModel]:
        query = self._build_get_query(*conditions, limit=limit)
        for option in options:
            query = query.options(selectinload(option))
        return self._detach_many(list(await self.session.scalars(query)))

    @final
    def _build_get_query(
        self,
        *conditions: ColumnExpressionArgument[bool],
        limit: int | None = DEFAULT_LIMIT,
    ):
        query = select(self.model_cls).where(*conditions)
        return query.limit(limit) if limit is not None else query

    @final
    async def _delete(self, *conditions: ColumnExpressionArgument[bool]) -> None:
        await self.session.execute(delete(self.model_cls).where(*conditions))
        await self.session.flush()

    @final
    async def _count(self, *conditions: ColumnExpressionArgument[bool]) -> int:
        result = await self.session.scalar(select(count(self.model_cls.id)).where(*conditions))
        return result or 0

    def _detach_many(self, instances: list[TModel]) -> list[TModel]:
        for instance in instances:
            self._detach(instance)
        return instances

    def _detach(self, instance: TModel | None) -> TModel | None:
        """Detach an eagerly loaded ORM graph before it can be cached or returned."""
        if instance is None:
            return None

        seen: set[int] = set()

        def visit(model: BaseModel) -> None:
            if id(model) in seen:
                return
            seen.add(id(model))

            state = inspect(model)
            for relation in state.mapper.relationships:
                if relation.key not in state.dict:
                    continue
                related = state.dict[relation.key]
                if related is None:
                    continue
                if relation.uselist:
                    for item in related:
                        visit(item)
                else:
                    visit(related)

            if state.session is not None:
                state.session.expunge(model)

        visit(instance)
        return instance
