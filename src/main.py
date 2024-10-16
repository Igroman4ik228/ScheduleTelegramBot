import asyncio
import logging
from logging.config import dictConfig

from injector import Injector, Module, provider, singleton

from background_service_pack.builder import BackgroundBuilder
from background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from config import Settings, settings
from database.db import engine
from database.redis.base import redis_client
from services.ad_service.ad_sender import AdService
from services.notify_service.notify import NotifyService
from services.parser_service.service import ParserService
from utils import constants

dictConfig(settings.logger_conf)

logger = logging.getLogger(__name__)


# Register DI
class AppModule(Module):

    @singleton
    @provider
    def provide_setting(self) -> Settings:
        return Settings()

    @provider
    def provide_parser_service(self, notify: NotifyService) -> ParserService:
        return ParserService(url=constants.SCHEDULE_URLS[1], time_span=10, notify=notify)

    @provider
    def provide_ad_service(self) -> AdService:
        return AdService(time_span=100)

    @singleton
    @provider
    def provide_notify_service(self, bot_manager: BotManager) -> NotifyService:
        return NotifyService(bot_manager)

    @provider
    def provide_builder(self, parser: ParserService) -> BackgroundBuilder:
        return BackgroundBuilder(parser=parser)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder.get_services())

    @singleton
    @provider
    def provide_bot(self, setting: Settings) -> BotManager:
        return BotManager(setting.BOT_TOKEN)


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

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
