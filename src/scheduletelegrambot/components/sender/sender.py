import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramAPIError

from scheduletelegrambot.database.db import DatabaseAlchemy, with_session
from scheduletelegrambot.database.repositories.users import UserRepository
from scheduletelegrambot.services.user import UserService
from scheduletelegrambot.utils.constants import SENDER_TIME_SLEEP

if TYPE_CHECKING:
    from aiogram import Bot
    from sqlalchemy.ext.asyncio import AsyncSession

    from scheduletelegrambot.database.models import UserModel


class TelegramSender:
    def __init__(
        self,
        db: DatabaseAlchemy,
        bot: Bot,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.bot = bot

    async def safe_send_range(self, tg_ids: list[int], message: str):
        self.logger.info("Start range send with message: %s", message)
        for tg_id in tg_ids:
            await self.safe_send_message(tg_id, message)
            await asyncio.sleep(SENDER_TIME_SLEEP)
            self.logger.debug("Sent message to %s: %s", tg_id, message)

    @with_session
    async def safe_send_message(self, tg_id: int, message: str, session: AsyncSession) -> None:
        user = await UserService(UserRepository(session)).get(tg_id)

        if self._is_valid_user(user):
            try:
                await self.bot.send_message(tg_id, message)
            except TelegramAPIError:
                self.logger.exception("Failed to send message to user %s", tg_id)
        else:
            self.logger.debug("Message skipped for inactive user %s", user)

    def _is_valid_user(self, user: UserModel | None) -> bool:
        if user is None:
            return False

        return not (user.is_ban or user.is_bot)
