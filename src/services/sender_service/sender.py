import asyncio
from logging import getLogger

from aiogram import Bot

from database.cache.repositories import CacheRepositoryService
from database.db import IDatabase, with_session
from database.models import UserModel
from database.repository import CachedRepository
from utils.constants import SENDER_TIME_SLEEP


class SenderService:
    def __init__(
        self, db: IDatabase, bot: Bot, cache_service: CacheRepositoryService
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.bot = bot
        self.cache_service = cache_service

    async def safe_send_range(self, tg_ids: list[int], message: str):
        self.logger.info(f"Start range send with message: {message}")
        for tg_id in tg_ids:
            await self.safe_send_message(tg_id, message)
            await asyncio.sleep(SENDER_TIME_SLEEP)
            self.logger.debug(f"Send {tg_id} : {message}")

    @with_session
    async def safe_send_message(self, tg_id: int, message: str, session=None):
        user = await CachedRepository(session, self.cache_service).users.get(
            tg_id
        )

        if self.is_valid_user(user):
            try:
                await self.bot.send_message(tg_id, message)
            except Exception as e:
                self.logger.debug(f"Failed send message to user {tg_id}\n{e}")
        else:
            self.logger.debug(
                f"Dont send message to {user}because user is banned or bot"
            )

    def is_valid_user(self, user: UserModel | None) -> bool:
        if user is None:
            return False

        if user.is_ban or user.is_bot:
            return False

        return True
