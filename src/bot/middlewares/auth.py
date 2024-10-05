from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.db import sessionmaker
from database.repositories.users import UserRepository


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: dict[str, Any],
    ) -> Any:
        user = message.from_user

        if not user:
            return await handler(message, data)

        async with sessionmaker() as session:
            user_rep = UserRepository(session)

            if await user_rep.exists(user.id):
                return await handler(message, data)

            new_user = await user_rep.create(
                first_name=user.first_name,
                user_name=user.username,
                telegram_id=user.id,
                last_name=user.last_name,
                is_bot=user.is_bot,
                is_premium=user.is_premium
            )
            self.logger.info(f"New user registration: {repr(new_user)}")

            return await handler(message, data)
