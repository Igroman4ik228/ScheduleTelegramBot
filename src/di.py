
from injector import Module, provider, singleton

from app.background_service_pack.builder import BackgroundBuilder
from app.background_service_pack.manager import BackgroundManager
from bot.bot import BotManager
from services.ad_service.ad_sender import AdService
from services.notify_service.notify import NotifyService
from services.parser_service.parser import ParserService
from services.sub_checker_service.sub_checker import SubCheckerService
from utils import constants
from utils.config import Settings


class AppModule(Module):

    @singleton
    @provider
    def provide_setting(self) -> Settings:
        return Settings()

    @provider
    def provide_parser_service(self, notify: NotifyService) -> ParserService:
        return ParserService(url=constants.SCHEDULE_URLS[1], time_span=10, notify=notify)

    @provider
    def provide_sub_checker_service(self, bot_manager: BotManager) -> SubCheckerService:
        return SubCheckerService(time_span=10, bot_manager=bot_manager)

    @singleton
    @provider
    def provide_notify_service(self, bot_manager: BotManager) -> NotifyService:
        return NotifyService(bot_manager)

    @provider
    def provide_builder(self, parser: ParserService, sub_checker: SubCheckerService) -> BackgroundBuilder:
        return BackgroundBuilder(parser=parser, sub_checker=sub_checker)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder.get_services())

    @singleton
    @provider
    def provide_bot(self, setting: Settings) -> BotManager:
        return BotManager(setting.BOT_TOKEN)
