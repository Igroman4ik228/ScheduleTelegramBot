from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import GroupModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GroupRepository(BaseRepositoryAlchemy[GroupModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GroupModel)
