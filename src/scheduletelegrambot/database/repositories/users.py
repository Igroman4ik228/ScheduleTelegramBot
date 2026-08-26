from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)
