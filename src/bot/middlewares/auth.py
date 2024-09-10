from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

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

        # if await user_exists(user.id):
        #     return await handler(message, data)

        logger.info(f"new user registration: {user.id}")

        # await add_user(session=session, user=user)

        return await handler(message, data)
