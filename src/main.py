import asyncio
import logging
from logging import Logger, getLogger
from logging.config import dictConfig

from injector import Injector, Module, inject, provider, singleton

from AdService.ad_sender import AdService
from BackgroundService.builder import BackgroundBuilder
from BackgroundService.manager import BackgroundManager
from bot.bot import BotManager
from config import Settings, settings
from database.db import engine
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

    # @provider
    # def provide_parser_service(self, logger: Logger, settings: Settings) -> ParserService:
    #     return ParserService(time_span=60, logger=logger, settings=settings)

    @provider
    def provide_parser_service(self, logger: Logger) -> ParserService:
        return ParserService(time_span=2, logger=logger)

    @provider
    def provide_ad_service(self, logger: Logger) -> AdService:
        return AdService(time_span=12, logger=logger)

    @provider
    def provide_builder(self, parser: ParserService, ad_sender: AdService) -> BackgroundBuilder:
        return BackgroundBuilder(parser, ad_sender)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder.get_services())

    @provider
    def provide_bot(self, setting: Settings) -> BotManager:
        return BotManager(setting.BOT_TOKEN)


async def main() -> None:
    injector = Injector(AppModule())
    try:
        #bot_manager = BotManager(settings.BOT_TOKEN)

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
