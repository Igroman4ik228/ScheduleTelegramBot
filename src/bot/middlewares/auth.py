from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.repositories.users import UserRepository

user_rep = UserRepository()

logger = getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: dict[str, Any],
    ) -> Any:
        user = message.from_user

        if not user:
            return await handler(message, data)

        if await user_rep.get(user.id):
            return await handler(message, data)

        logger.info(f"new user registration: {user.id}")
        await user_rep.create(user.username, user.id)

        return await handler(message, data)
