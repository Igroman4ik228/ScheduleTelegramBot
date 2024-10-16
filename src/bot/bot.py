from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers import register_routers
from bot.middlewares import register_middlewares
from database.redis.base import redis_client


class BotManager:
    def __init__(self, token):
        self.logger = getLogger(__name__)
        self.bot = Bot(token, default=DefaultBotProperties(parse_mode="HTML"))
        self.dp = Dispatcher(
            storage=RedisStorage(redis_client)
        )

    async def start(self):
        await self.bot.delete_webhook(drop_pending_updates=True)

        self.dp.startup.register(self._on_startup)
        self.dp.shutdown.register(self._on_shutdown)

        await self.dp.start_polling(self.bot)

    def _on_startup(self):
        register_middlewares(self.dp)
        register_routers(self.dp)

    async def _on_shutdown(self):
        await self.bot.session.close()
