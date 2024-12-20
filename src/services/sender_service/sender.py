import asyncio
from logging import getLogger
from aiogram import Bot


class SenderService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = getLogger(__class__.__name__)

    async def send_range(self, message: str, users_id: list[int]):
        # ToDo: integrate safe send
        self.logger.info(f"Start range send with message: {message}")
        for user_id in users_id:
            try:
                await self.bot.send_message(user_id, message)
            except Exception as e:
                self.logger.info(f"Failed send message to user {user_id}\n{e}")
            await asyncio.sleep(0.3)
            self.logger.info(f"Send {user_id} : {message}")

    async def safe_send_message(user_id, message):
        # ToDo create safe method to send message with out any errors
        pass

