import asyncio
import sys
from contextlib import suppress

from injector import Injector

from app.background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from container import create_injector
from database.cache.base import ICache
from database.cache.repositories import CacheService
from database.db import DatabaseAlchemy
from services.loader_service.default_schedule import DefaultScheduleLoader
from settings import Settings
from utils.logger import LOGGER_CONFIG_EXTRA_FILES, logger_configure


class App:
    def __init__(self, injector: Injector):
        self.injector = injector
        self.settings = self.injector.get(Settings)
        self.db = self.injector.get(DatabaseAlchemy)
        self.cache = self.injector.get(ICache)
        self.cache_repository = self.injector.get(CacheService)
        self.bot_manager = self.injector.get(BotManager)
        self.service_manager = self.injector.get(BackgroundManager)
        self.default_schedule_loader = self.injector.get(DefaultScheduleLoader)

    async def start(self):
        logger_configure(LOGGER_CONFIG_EXTRA_FILES)

        await self.default_schedule_loader.process_all_files()

        await asyncio.gather(
            self.bot_manager.start(),
            self.service_manager.start_services(),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.dispose()
        await self.cache.close()


async def main():
    # For Unix-based systems
    stop_event = asyncio.Event()
    unix_signal_handler(stop_event)

    injector = create_injector()
    async with App(injector) as app:
        start_task = asyncio.create_task(app.start())
        await stop_event.wait()
        start_task.cancel()
        with suppress(asyncio.CancelledError):
            await start_task


def unix_signal_handler(stop_event: asyncio.Event):
    if sys.platform != "win32":
        import signal

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        exit(1)
