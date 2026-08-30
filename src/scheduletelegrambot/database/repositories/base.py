from __future__ import annotations

from typing import TYPE_CHECKING, Any, final

from sqlalchemy import ColumnExpressionArgument, CursorResult, delete, select, update
from sqlalchemy.orm import InstrumentedAttribute, QueryableAttribute, joinedload, selectinload
from sqlalchemy.sql.functions import count

from scheduletelegrambot.database.models.base import BaseModel
from scheduletelegrambot.utils.logger import LoggerMixin

if TYPE_CHECKING:
    from collections.abc import Mapping

    from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_LIMIT = 10_000


class BaseRepositoryAlchemy[TModel: BaseModel](LoggerMixin):
    def __init__(self, session: AsyncSession, model_cls: type[TModel]) -> None:
        self._session = session
        self.model_cls = model_cls

    async def create(self, **values: Any) -> TModel:
        instance = self.model_cls(**values)
        self._session.add(instance)

        await self._session.flush()
        return instance

    async def get_by_id(self, object_id: int) -> TModel | None:
        return await self._session.get(self.model_cls, object_id)

    async def update(self, instance: TModel) -> TModel:
        merged = await self._session.merge(instance)

        await self._session.flush()
        return merged

    async def delete(self, instance: TModel) -> None:
        await self._session.delete(instance)
        await self._session.flush()

    async def execute_update(
        self,
        *conditions: ColumnExpressionArgument[bool],
        values: Mapping[InstrumentedAttribute[Any], Any],
    ) -> CursorResult[Any]:
        if not values:
            raise ValueError("execute_update requires at least one value")

        connection = await self._session.connection()

        return await connection.execute(update(self.model_cls).where(*conditions).values(values))

    async def execute_delete(
        self, *conditions: ColumnExpressionArgument[bool]
    ) -> CursorResult[Any]:
        connection = await self._session.connection()

        return await connection.execute(delete(self.model_cls).where(*conditions))

    async def get_one(
        self,
        *conditions: ColumnExpressionArgument[bool],
        options: tuple[QueryableAttribute[Any], ...] = (),
    ) -> TModel | None:
        query = self._build_get_query(*conditions, limit=1)

        for option in options:
            query = query.options(joinedload(option))

        return await self._session.scalar(query)

    async def get_many(
        self,
        *conditions: ColumnExpressionArgument[bool],
        options: tuple[QueryableAttribute[Any], ...] = (),
        limit: int | None = DEFAULT_LIMIT,
    ) -> list[TModel]:
        query = self._build_get_query(*conditions, limit=limit)

        for option in options:
            query = query.options(selectinload(option))

        return list(await self._session.scalars(query))

    @final
    def _build_get_query(
        self,
        *conditions: ColumnExpressionArgument[bool],
        limit: int | None = DEFAULT_LIMIT,
    ):
        query = select(self.model_cls).where(*conditions)
        return query.limit(limit) if limit is not None else query

    @final
    async def count(self, *conditions: ColumnExpressionArgument[bool]) -> int:
        result = await self._session.scalar(select(count(self.model_cls.id)).where(*conditions))
        return result or 0
