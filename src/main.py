import asyncio

from injector import Injector

from app.background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from database.db import engine
from database.redis.base import redis_client
from di import AppModule
from utils.config import settings


async def main():
    injector = Injector(AppModule())
    try:
        bot_manager = injector.get(BotManager)
        service_manager = injector.get(BackgroundManager)

        await asyncio.gather(
            bot_manager.start(),
            service_manager.start_services()
        )

    finally:
        await engine.dispose()
        await redis_client.aclose()


if __name__ == "__main__":
    settings.logger.configure()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
