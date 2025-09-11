from aiogram import Bot, Dispatcher

from app.factory_pack.parser_factory import ParserFactory
from bot.handlers import register_routers
from bot.middlewares import register_middlewares
from database.cache.profile_cache import ProfileCache
from database.cache.repositories import CacheRepositoryService
from database.db import DatabaseAlchemy
from services.sender_service.sender import SenderService
from utils.config import Settings


class BotManager:
    def __init__(
        self,
        bot: Bot,
        dp: Dispatcher,
        settings: Settings,
        db: DatabaseAlchemy,
        sender_service: SenderService,
        profile_cache: ProfileCache,
        cache_service: CacheRepositoryService,
        parser_factory: ParserFactory,
    ):
        self.bot = bot
        self.dp = dp
        self.settings = settings
        self.db = db
        self.sender_service = sender_service
        self.profile_cache = profile_cache
        self.cache_service = cache_service
        self.parser_factory = parser_factory

    async def start(self):
        await self.bot.delete_webhook(drop_pending_updates=True)

        self.dp.startup.register(self._on_startup)
        self.dp.shutdown.register(self._on_shutdown)

        await self.dp.start_polling(
            self.bot, allowed_updates=["message", "callback_query"]
        )

    def _on_startup(self):
        self.dp["settings"] = self.settings
        self.dp["db"] = self.db
        self.dp["sender_service"] = self.sender_service
        self.dp["profile_cache"] = self.profile_cache
        self.dp["cache_service"] = self.cache_service
        self.dp["parser_factory"] = self.parser_factory

        register_middlewares(self.dp)
        register_routers(self.dp)

    async def _on_shutdown(self):
        await self.bot.session.close()
        await self.dp.storage.close()
