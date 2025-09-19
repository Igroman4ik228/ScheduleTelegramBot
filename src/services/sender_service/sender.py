import asyncio
from logging import getLogger

from aiogram import Bot

from database.cache.repositories import CacheService
from database.db import DatabaseAlchemy
from utils.constants import SENDER_TIME_SLEEP


class SenderService:
    def __init__(
        self,
        db: DatabaseAlchemy,
        bot: Bot,
        cache_service: CacheService,
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

    async def safe_send_message(self, tg_id: int, message: str) -> bool:
        try:
            await self.bot.send_message(tg_id, message)
            self.logger.info(f"Message send to tg_id={tg_id}")
            return True
        except Exception as e:
            self.logger.debug(f"Failed send message to user tg_id={tg_id}:{e}")
            return False
