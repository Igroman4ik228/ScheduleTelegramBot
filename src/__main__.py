import asyncio
import sys
from contextlib import suppress
from logging import getLogger

from injector import Injector

from app.background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from container import create_injector
from database.cache.base import ICache
from database.cache.repositories import CacheRepositoryService
from database.db import DatabaseAlchemy
from database.uow import UoW
from services.loader_service.default_schedule import DefaultScheduleLoader
from settings import Settings
from utils.logger import LOGGER_CONFIG, logger_configure


class App:
    def __init__(self, injector: Injector):
        self.injector = injector
        self.settings = self.injector.get(Settings)
        self.db = self.injector.get(DatabaseAlchemy)
        self.cache = self.injector.get(ICache)
        self.cache_repository = self.injector.get(CacheRepositoryService)
        self.bot_manager = self.injector.get(BotManager)
        self.service_manager = self.injector.get(BackgroundManager)
        self.default_schedule_loader = self.injector.get(DefaultScheduleLoader)

    async def start(self):
        logger_configure(LOGGER_CONFIG)
        logger = getLogger(self.__class__.__name__)
        async with UoW(self.db.sessionmaker) as uow:
            users = await uow.users.get_many_with_all()
            logger.info(f"users={users}")

            # user.first_name = "123"

            # await uow.users.update(user)

            # user = UserModel(first_name="123", telegram_id=1)

            # await uow.commit()

        # rep = BaseRepositoryAlchemy(session, UserModel)

        # user = await rep._get(UserModel.id == 2, detach=False)
        # logger.info(f"user={user}")
        # user.first_name = "132"
        # await session.merge(user)
        # await session.commit()
        # is_user_update = await rep._update(
        #     UserModel.first_name == "Ники11тосик"
        # )
        # logger.info(f"user_update={is_user_update}")

        # user1 = await rep._get(UserModel.id == 2)

        # logger.info(f"user1={user1}")

        # async with self.db.get_session() as session:
        #     rep = BaseRepositoryAlchemy(session, UserModel)

        #     user = await rep._get(UserModel.user_name == "Notoxikk")
        #     logger.info(f"user={user}")

        # await asyncio.gather(
        #     self.bot_manager.start(),
        #     self.service_manager.start_services(),
        # )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.dispose()
        await self.cache.close()


async def main():
    # For Unix-based systems
    unix_signal_handler()

    injector = create_injector()
    stop_event = asyncio.Event()
    async with App(injector) as app:
        start_task = asyncio.create_task(app.start())
        await stop_event.wait()
        start_task.cancel()
        with suppress(asyncio.CancelledError):
            await start_task


def unix_signal_handler():
    if sys.platform != "win32":
        import signal

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, loop.stop)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        exit(1)
