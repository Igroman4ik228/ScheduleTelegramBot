from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from scheduletelegrambot.bot.handlers import register_routers
from scheduletelegrambot.bot.middlewares import register_middlewares
from scheduletelegrambot.settings import Settings


class BotManager:
    def __init__(self, settings: Settings) -> None:
        self._bot = Bot(
            settings.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        self._dispatcher = Dispatcher(storage=RedisStorage.from_url(settings.cache.url(db=1)))
        self.settings = settings

    async def start_polling(self) -> None:
        register_middlewares(self._dispatcher, self.settings)
        register_routers(self._dispatcher, self.settings)

        await self._bot.delete_webhook(drop_pending_updates=True)

        await self._dispatcher.start_polling(
            self._bot, allowed_updates=["message", "callback_query"]
        )

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dispatcher
