import asyncio
from logging import getLogger
from bot.bot import BotManager
from database.db import sessionmaker
from database.repository import Repository


class SenderService:

    def __init__(self, bot_manager: BotManager):
        self.bot = bot_manager.bot
        self.logger = getLogger(__class__.__name__)

    async def safe_send_range(self, message: str, tg_ids: list[int]):
        self.logger.info(f"Start range send with message: {message}")
        for tg_id in tg_ids:
            try:
                await self.safe_send_message(tg_id, message)
            except Exception as e:
                self.logger.info(f"Failed send message to user {tg_id}\n{e}")
            await asyncio.sleep(0.3)
            self.logger.info(f"Send {tg_id} : {message}")

    async def safe_send_message(self, tg_id, message):
        if await self.check_user(tg_id):
            await self.bot.send_message(tg_id, message)

    async def check_user(self, tg_id: int):
        async with sessionmaker() as session:
            repo = Repository(session)
            user = await repo.users.get(tg_id)

            if not user.is_ban and not user.is_bot:
                return True
            return False
