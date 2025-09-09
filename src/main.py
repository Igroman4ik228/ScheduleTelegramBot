import asyncio
import signal
import sys
from contextlib import suppress

from injector import Injector

from app.background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from database.cache.base import ICache
from database.db import IDatabase
from di import AppModule
from services.loader_service.default_schedule import DefaultScheduleLoader
from utils.config import Settings


class App:
    def __init__(self, injector: Injector):
        self.injector = injector
        self.settings = self.injector.get(Settings)
        self.db = self.injector.get(IDatabase)
        self.cache = self.injector.get(ICache)
        self.bot_manager = self.injector.get(BotManager)
        self.service_manager = self.injector.get(BackgroundManager)
        self.default_schedule_loader = self.injector.get(DefaultScheduleLoader)

    async def start(self):
        self.settings.logger.configure()

        await self.db.create_tables()

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
    injector = Injector(AppModule())
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # For Linux
    if sys.platform != "win32":
        for s in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(s, stop_event.set)

    async with App(injector) as app:
        start_task = asyncio.create_task(app.start())
        await stop_event.wait()
        start_task.cancel()
        with suppress(asyncio.CancelledError):
            await start_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        exit(1)
