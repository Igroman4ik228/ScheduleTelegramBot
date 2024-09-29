from logging import getLogger

from sqlalchemy import select

from database.db import sessionmaker
from database.models.users import UserModel
from database.repositories.groups import GroupRepository

logger = getLogger(__name__)


class UserRepository:
    async def create(self, name: str, telegram_id: int, group_name: str = None) -> None:
        group = None
        if group_name:
            group_repo = GroupRepository()
            group = await group_repo.get_by_name(group_name)

        user = UserModel(
            name=name,
            telegram_id=telegram_id,
            group_id=group.id if group else None
        )
        async with sessionmaker() as session:
            session.add(user)
            await session.commit()

    async def get(self, telegram_id: int) -> UserModel | None:
        async with sessionmaker() as session:
            user_query = await session.execute(
                select(UserModel)
                .filter_by(telegram_id=telegram_id)
            )
        return user_query.scalar_one_or_none()

    async def get_all(self) -> list[UserModel]:
        async with sessionmaker() as session:
            users_query = await session.execute(select(UserModel))
        return users_query.scalars().all()

    async def delete(self, telegram_id: int) -> None:
        user = self.get(telegram_id)
        if not user:
            logger.warning(f"User {telegram_id} not found for delete")
            return

        async with sessionmaker() as session:
            await session.delete(user)
            await session.commit()

    async def update(self, user: UserModel) -> None:
        existing_user = await self.get(user.telegram_id)
        if not existing_user:
            logger.warning(f"User {user.telegram_id} not found for update")
            return

        async with sessionmaker() as session:
            existing_user.name = user.name
            await session.commit()
