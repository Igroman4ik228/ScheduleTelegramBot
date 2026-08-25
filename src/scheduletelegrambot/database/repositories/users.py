from typing import TYPE_CHECKING

from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)
