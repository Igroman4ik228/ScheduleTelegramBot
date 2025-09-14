from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import BaseModel
from utils.logger import LoggerMixin

TModel = TypeVar("Model", bound=BaseModel)


# todo: code this
class BaseRepositoryAlchemy[TModel](LoggerMixin):
    def __init__(self, session: AsyncSession, model: type[TModel]):
        self.session = session
        self.type_model = model


class RepositoryException(Exception): ...
