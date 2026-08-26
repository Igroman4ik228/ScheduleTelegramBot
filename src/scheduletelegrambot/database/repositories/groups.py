from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import GroupModel
from scheduletelegrambot.database.repositories.base import (
    BaseRepositoryAlchemy,
)


class GroupRepository(BaseRepositoryAlchemy[GroupModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GroupModel)
