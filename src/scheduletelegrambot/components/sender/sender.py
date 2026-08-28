import asyncio
from logging import getLogger

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from dishka import AsyncContainer

from scheduletelegrambot.schemas.user import UserBaseSchema
from scheduletelegrambot.services.user import UserService
from scheduletelegrambot.utils.constants import SENDER_TIME_SLEEP


class TelegramSender:
    def __init__(
        self,
        container: AsyncContainer,
        bot: Bot,
    ) -> None:
        self.logger = getLogger(self.__class__.__name__)
        self.container = container
        self.bot = bot

    async def safe_send_range(self, tg_ids: list[int], message: str) -> None:
        self.logger.info("Start range send with message: %s", message)
        for tg_id in tg_ids:
            await self.safe_send_message(tg_id, message)
            await asyncio.sleep(SENDER_TIME_SLEEP)
            self.logger.debug("Sent message to %s: %s", tg_id, message)

    async def safe_send_message(self, tg_id: int, message: str) -> None:
        async with self.container() as request_container:
            users = await request_container.get(UserService)
            user = await users.find(tg_id)

        if self._is_valid_user(user):
            try:
                await self.bot.send_message(tg_id, message)
            except TelegramAPIError:
                self.logger.exception("Failed to send message to user %s", tg_id)
        else:
            self.logger.debug("Message skipped for inactive user %s", user)

    def _is_valid_user(self, user: UserBaseSchema | None) -> bool:
        if user is None:
            return False

        return not (user.is_ban or user.is_bot)
