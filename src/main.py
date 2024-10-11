import asyncio
import logging
from logging import Logger
from logging.config import dictConfig

from injector import Injector, Module, provider, singleton

from ad_service.ad_sender import AdService
from background_service_pack.builder import BackgroundBuilder
from background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from config import Settings, settings
from database.db import engine, sessionmaker
from database.repositories.groups import GroupRepository
from notify_service.notify import NotifyService
from parser_service.parser import ParserService
from parser_service.week import Week
from utils import constants

dictConfig(settings.logger_conf)

logger = logging.getLogger(__name__)


# Register DI
class AppModule(Module):

    @singleton
    @provider
    def provide_setting(self) -> Settings:
        return Settings()

    # TODO: Edit time_span for realization logic or production
    @provider
    def provide_parser_service(self, notify: NotifyService) -> ParserService:
        return ParserService(url=constants.SCHEDULE_URLS[1], time_span=10*60, notify=notify)

    # TODO: Edit time_span for realization logic or production
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


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
