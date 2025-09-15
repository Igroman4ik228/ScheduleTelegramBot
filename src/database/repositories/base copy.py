from typing import TypeVar

from sqlalchemy import ColumnExpressionArgument, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import BaseModel
from utils.logger import LoggerMixin

TModel = TypeVar("TModel", bound=BaseModel)


class BaseRepositoryAlchemy[TModel](LoggerMixin):
    def __init__(self, session: AsyncSession, type_model: type[TModel]):
        self.session = session
        self.type_model = type_model

    def _create(self, model: TModel):
        self.session.add(model)

    async def _get(self, *conditions: ColumnExpressionArgument[any]):
        return await self.session.scalar(
            select(self.type_model).where(*conditions)
        )

    # todo: type id
    async def _get_by_id(self, id: int):
        return await self.session.get(self.type_model, id)

    async def _get_all(self, *conditions: ColumnExpressionArgument[any]):
        return await list(
            self.session.scalars(select(self.type_model).where(*conditions))
        )

    async def _update(
        self,
        conditions: list[ColumnExpressionArgument[any]] = [],
        load_result: bool = False,
    ): ...

    async def _delete(self, *conditions: ColumnExpressionArgument[any]):
        result = await self.session.execute(
            delete(self.type_model).where(*conditions)
        )
        await self.session.commit()
        return result.rowcount > 0
