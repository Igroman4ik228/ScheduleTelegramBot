import asyncio
import signal

from injector import Injector

from app.background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from database.db import db_helper
from database.redis.base import redis_client
from di import AppModule
from services.loader_service.default_schedule import DefaultScheduleLoader


class App:
    def __init__(self, injector: Injector):
        self.injector = injector

    async def start(self):
        bot_manager = self.injector.get(BotManager)
        service_manager = self.injector.get(BackgroundManager)

        await DefaultScheduleLoader().process_all_files()

        await asyncio.gather(
            bot_manager.start(),
            service_manager.start_services(),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await db_helper.dispose()
        await redis_client.aclose()


async def main():
    injector = Injector(AppModule())
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    # For linux
    try:
        for s in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(s, stop_event.set)
    except NotImplementedError:
        pass

    async with App(injector) as app:
        start_task = asyncio.create_task(app.start())
        await stop_event.wait()
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        exit(1)
