from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.factory_pack.parser_factory import ParserFactory
from bot.handlers import register_routers
from bot.middlewares import register_middlewares
from utils.config import settings


class BotManager:
    def __init__(self, bot: Bot, parser_factory: ParserFactory):
        self.bot = bot
        self.dp = Dispatcher(
            storage=RedisStorage.from_url(url=settings.redis.url(db=1))
        )
        self.parser_factory = parser_factory

    async def start(self):
        await self.bot.delete_webhook(drop_pending_updates=True)

        self.dp.startup.register(self._on_startup)
        self.dp.shutdown.register(self._on_shutdown)

        await self.dp.start_polling(
            self.bot, allowed_updates=["message", "callback_query"]
        )

    def _on_startup(self):
        self.dp["parser_factory"] = self.parser_factory

        register_middlewares(self.dp)
        register_routers(self.dp)

    async def _on_shutdown(self):
        await self.bot.session.close()
        await self.dp.storage.close()
