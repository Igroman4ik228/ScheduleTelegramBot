from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.database.repositories.base import DEFAULT_LIMIT, BaseRepositoryAlchemy


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)

    async def get_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        return await self.get_one(UserModel.telegram_id == telegram_id)

    async def get_with_group(self, telegram_id: int) -> UserModel | None:
        return await self.get_one(
            UserModel.telegram_id == telegram_id,
            options=(UserModel.group,),
        )

    async def get_with_all(self, telegram_id: int) -> UserModel | None:
        return await self.get_one(
            UserModel.telegram_id == telegram_id,
            options=(UserModel.group, UserModel.subscribe),
        )

    async def list_all(self) -> list[UserModel]:
        return await self.get_many()

    async def list_by_group_id(self, group_id: int) -> list[UserModel]:
        return await self.get_many(UserModel.group_id == group_id)

    async def list_without_group(self) -> list[UserModel]:
        return await self.get_many(UserModel.group_id.is_(None))

    async def list_notification_recipients(self) -> list[UserModel]:
        return await self.get_many(
            UserModel.is_notify.is_(True),
            UserModel.is_ban.is_(False),
            UserModel.is_bot.is_(False),
            options=(UserModel.group,),
        )

    async def list_with_subscribe(self, limit: int = DEFAULT_LIMIT) -> list[UserModel]:
        return await self.get_many(
            options=(UserModel.subscribe, UserModel.group),
            limit=limit,
        )

    async def execute_update_group(self, telegram_id: int, group_id: int) -> bool:
        result = await self.execute_update(
            UserModel.telegram_id == telegram_id,
            values={UserModel.group_id: group_id},
        )
        return result.rowcount > 0

    async def execute_update_ban(self, telegram_id: int, is_ban: bool) -> bool:
        result = await self.execute_update(
            UserModel.telegram_id == telegram_id,
            values={UserModel.is_ban: is_ban},
        )
        return result.rowcount > 0

    async def execute_update_notify(self, telegram_id: int, is_notify: bool) -> bool:
        result = await self.execute_update(
            UserModel.telegram_id == telegram_id,
            values={UserModel.is_notify: is_notify},
        )
        return result.rowcount > 0

    async def execute_update_time_shown(self, telegram_id: int, is_time_shown: bool) -> bool:
        result = await self.execute_update(
            UserModel.telegram_id == telegram_id,
            values={UserModel.is_time_shown: is_time_shown},
        )
        return result.rowcount > 0

    async def execute_update_subscribe(
        self, telegram_id: int, subscribe_id: int | None, subscribe_end_time: datetime | None
    ) -> bool:
        result = await self.execute_update(
            UserModel.telegram_id == telegram_id,
            values={
                UserModel.subscribe_id: subscribe_id,
                UserModel.subscribe_end_time: subscribe_end_time,
            },
        )
        return result.rowcount > 0
