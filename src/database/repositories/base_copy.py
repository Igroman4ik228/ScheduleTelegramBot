from typing import Any, Generic, TypeVar, cast, final

from sqlalchemy import (
    ColumnExpressionArgument,
    delete,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, joinedload, selectinload
from sqlalchemy.sql.functions import count

from database.models.base import BaseModel
from utils.logger import LoggerMixin

TModel = TypeVar("TModel", bound=BaseModel)


DEFAULT_LIMIT = 10000


class BaseRepositoryAlchemy(Generic[TModel], LoggerMixin):
    def __init__(self, session: AsyncSession, model_cls: type[TModel]):
        self.session = session
        self.model_cls = model_cls

    @final
    async def _get_by_id(self, id: int, detach: bool = True) -> TModel | None:
        instance = await self.session.get(self.model_cls, id)
        if instance and detach:
            self.session.expunge(instance)
        return instance

    @final
    async def _get(
        self,
        *conditions: ColumnExpressionArgument[bool],
        options: tuple[QueryableAttribute[TModel], ...] = (),
        detach: bool = True,
    ) -> TModel | None:
        query = self._build_get_query(*conditions, limit=1)
        for option in options:
            query = query.options(joinedload(option))

        instance = await self.session.scalar(query)
        if instance and detach:
            self.session.expunge(instance)
        return instance

    @final
    async def _get_many(
        self,
        *conditions: ColumnExpressionArgument[bool],
        options: tuple[QueryableAttribute[Any], ...] = (),
        limit: int = DEFAULT_LIMIT,
    ) -> list[TModel]:
        query = self._build_get_query(*conditions, limit=limit)
        for option in options:
            query = query.options(selectinload(option))

        return list(await self.session.scalars(query))

    @final
    def _build_get_query(
        self,
        *conditions: ColumnExpressionArgument[bool],
        limit: int = DEFAULT_LIMIT,
    ):
        query = select(self.model_cls).where(*conditions)
        if limit is not None:
            query = query.limit(limit)
        return query

    @final
    async def _update(
        self,
        *conditions: ColumnExpressionArgument[bool],
        **values: Any,
    ) -> bool:
        if not values:
            conditions_str = (
                " AND ".join(str(condition) for condition in conditions)
                or "no conditions"
            )
            self.logger.warning(
                f"UPDATE {self.model_cls.__name__} don't execute because values is not valid "
                f"with conditions={conditions_str}, values={values}"
            )
            return False

        result = await self.session.execute(
            update(self.model_cls).where(*conditions).values(**values)
        )
        # todo: flush or commit?
        await self.session.commit()
        # await self.session.flush()

        if result.rowcount == 0:
            conditions_str = (
                " AND ".join(str(condition) for condition in conditions)
                or "no conditions"
            )
            self.logger.warning(
                f"UPDATE {self.model_cls.__name__} did not affect any rows "
                f"with conditions={conditions_str}, values={values}"
            )
            return False

        return True

    @final
    async def _delete(
        self, *conditions: ColumnExpressionArgument[bool]
    ) -> bool:
        result = await self.session.execute(
            delete(self.model_cls).where(*conditions)
        )
        # todo: flush or commit?
        await self.session.commit()
        # await self.session.flush()

        if result.rowcount == 0:
            conditions_str = (
                " AND ".join(str(condition) for condition in conditions)
                or "no conditions"
            )
            self.logger.warning(
                f"DELETE {self.model_cls.__name__} did not affect any rows "
                f"with conditions={conditions_str}"
            )
            return False

        return True

    @final
    async def _count(self) -> int:
        return cast(
            int,
            await self.session.scalar(select(count(self.model_cls.id))),
        )
