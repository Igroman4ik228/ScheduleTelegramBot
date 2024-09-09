from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from .handlers import register_routers
from .middlewares import register_middlewares

logger = getLogger(__name__)


class BotManager:
    def __init__(self, token):
        self.bot = Bot(token, default=DefaultBotProperties(parse_mode="HTML"))
        self.dp = Dispatcher()

    async def start(self):
        try:
            self.dp.startup.register(self._on_startup)
            self.dp.shutdown.register(self._on_shutdown)

            await self.dp.start_polling(self.bot, skip_updates=True)
        except Exception as e:
            logger.error(f"Ошибка {e}", exc_info=True)

    def _on_startup(self):
        register_middlewares(self.dp)
        register_routers(self.dp)

    async def _on_shutdown(self):
        await self.bot.session.close()
