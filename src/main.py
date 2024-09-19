import asyncio
import logging
from logging import Logger, getLogger
from logging.config import dictConfig

from injector import Injector, Module, inject, provider, singleton

import constants
from AdService.ad_sender import AdService
from BackgroundServicePack.builder import BackgroundBuilder
from BackgroundServicePack.manager import BackgroundManager
from bot.bot import BotManager
from config import Settings, settings
from database.db import engine
from NotifyService.notify import NotifyService
from ParserService.parser import ParserService

dictConfig(settings.logger_conf)
logger = getLogger(__name__)


# Register DI
class AppModule(Module):

    @singleton
    @provider
    def provide_setting(self) -> Settings:
        return Settings()

    @singleton
    @provider
    def provide_logger(self) -> Logger:
        logger = logging.getLogger(__name__)
        return logger

    # TODO: Edit time_span for realization logic or production
    @provider
    def provide_parser_service(self, logger: Logger, notify: NotifyService) -> ParserService:
        return ParserService(url=constants.SCHEDULE_URLS[1], time_span=2, logger=logger, notify=notify)

    # TODO: Edit time_span for realization logic or production
    @provider
    def provide_ad_service(self, logger: Logger) -> AdService:
        return AdService(time_span=12, logger=logger)

    @singleton
    @provider
    def provide_notify_service(self, logger: Logger) -> NotifyService:
        return NotifyService(logger=logger)

    @provider
    def provide_builder(self, parser: ParserService, ad_sender: AdService) -> BackgroundBuilder:
        return BackgroundBuilder(parser=parser, ad_sender=ad_sender)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder.get_services())

    @provider
    def provide_bot(self, setting: Settings) -> BotManager:
        return BotManager(setting.BOT_TOKEN)


async def main() -> None:
    injector = Injector(AppModule())
    try:
        bot_manager = injector.get(BotManager)
        service_manager = injector.get(BackgroundManager)

        await asyncio.gather(bot_manager.start(), service_manager.start_services())
    finally:
        await engine.dispose()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
