from __future__ import annotations

from aiogram import Bot, Dispatcher

from scheduletelegrambot.bot.handlers import register_routers
from scheduletelegrambot.bot.middlewares import register_middlewares
from scheduletelegrambot.settings import Settings


class BotManager:
    def __init__(self, bot: Bot, dp: Dispatcher, settings: Settings) -> None:
        self.bot = bot
        self.dp = dp
        self.settings = settings
        self._configured = False

    def configure(self) -> None:
        if self._configured:
            return

        register_middlewares(self.dp, self.settings)
        register_routers(self.dp, self.settings)

        self._configured = True

    async def start(self) -> None:
        await self.bot.delete_webhook(drop_pending_updates=True)

        await self.dp.start_polling(self.bot, allowed_updates=["message", "callback_query"])
