from __future__ import annotations

from datetime import datetime, timedelta
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import BaseMiddleware

from database.uow import CachedUoW
from helpers.text import quote_html_range

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Dict

    from aiogram.types import TelegramObject
    from aiogram.types.user import User as AiogramUser

    from database.models import UserModel


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: AiogramUser = data["event_from_user"]
        uow: CachedUoW = data["uow"]
        existing_user = await uow.rep.users.get_with_all(tg_user.id)
        if existing_user:
            data["user"] = existing_user
            return await handler(event, data)

        data["user"] = await self._create_user(tg_user, uow)
        return await handler(event, data)

    async def _create_user(
        self,
        tg_user: AiogramUser,
        uow: CachedUoW,
    ) -> UserModel:
        subscribes = await uow.rep.subscribes.get_many_by_price(0)
        if not subscribes:
            raise ValueError("No free subscribes available for new users")
        trail_subscribe = subscribes[0]
        subscribe_end_time = datetime.now() + timedelta(
            days=trail_subscribe.duration_days
        )

        first_name, last_name = quote_html_range(
            [tg_user.first_name, tg_user.last_name]
        )

        new_user = UserModel(
            first_name=first_name,
            last_name=last_name,
            user_name=tg_user.username,
            telegram_id=tg_user.id,
            is_bot=tg_user.is_bot,
            is_premium=tg_user.is_premium,
            subscribe_id=trail_subscribe.id,
            subscribe_end_time=subscribe_end_time,
        )
        await uow.commit(new_user)

        # # Get must be called after create to ensure relations are loaded
        new_user = await uow.rep.users.get_with_all(new_user.telegram_id)

        if new_user is None:
            raise ValueError("Failed to create new user")

        self.logger.info(f"Successfully registered new user: {new_user}")
        return new_user
