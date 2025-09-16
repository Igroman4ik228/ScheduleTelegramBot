from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel
from database.repositories.base_copy import DEFAULT_LIMIT, BaseRepositoryAlchemy


class UserRepository(BaseRepositoryAlchemy[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    async def get_with_group(self, telegram_id: int, detach: bool = True):
        return await self._get(
            UserModel.telegram_id == telegram_id,
            options=(UserModel.group,),
            detach=detach,
        )

    async def get_with_subscribe(self, telegram_id: int, detach: bool = True):
        return await self._get(
            UserModel.telegram_id == telegram_id,
            options=(UserModel.subscribe,),
            detach=detach,
        )

    async def get_with_all(self, telegram_id: int, detach: bool = True):
        return await self._get(
            UserModel.telegram_id == telegram_id,
            options=(
                UserModel.group,
                UserModel.subscribe,
            ),
            detach=detach,
        )

    async def get_many_with_all(
        self, limit: int = DEFAULT_LIMIT, detach: bool = True
    ):
        return await self._get_many(
            options=(
                UserModel.group,
                UserModel.subscribe,
            ),
            limit=limit,
            detach=detach,
        )

    async def update(self, user: UserModel):
        # clear_cache()
        await self.session.merge(user)
