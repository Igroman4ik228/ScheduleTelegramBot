from datetime import timedelta
from enum import Enum

from injector import Module, provider, singleton

from app.background_service_pack.builder import BackgroundBuilder
from app.background_service_pack.manager import BackgroundManager
from app.factory_pack.parser_factory import ParserFactory
from bot.bot import BotManager
from services.notify_service.notify import NotifyService
from services.parser_service.parser import ParserService
from services.sender_service.sender import SenderService
from services.sub_checker_service.sub_checker import SubCheckerService
from utils.config import Settings

SCHEDULE_URLS = [
    "https://menu.sttec.yar.ru/timetable/rasp_first.html",
    "https://menu.sttec.yar.ru/timetable/rasp_second.html"
]


class TimeSpan(Enum):
    SUB_CHECKER = timedelta(seconds=60).seconds
    PARSER = timedelta(seconds=10).seconds


class AppModule(Module):

    @singleton
    @provider
    def provide_setting(self) -> Settings:
        return Settings()

    @provider
    def provide_sender_service(self, bot_manager: BotManager) -> SenderService:
        return SenderService(bot_manager=bot_manager)

    @provider
    def provide_parser_factory(self, notify: NotifyService) -> ParserFactory:
        return ParserFactory(additional_param=SCHEDULE_URLS, time_span=TimeSpan.PARSER.value, notify=notify)

    @provider
    def provide_sub_checker_service(self, sender: SenderService) -> SubCheckerService:
        return SubCheckerService(
            time_span=TimeSpan.SUB_CHECKER.value,
            sender=sender
        )

    @singleton
    @provider
    def provide_notify_service(self, bot_manager: BotManager) -> NotifyService:
        return NotifyService(bot_manager)

    @provider
    def provide_builder(
        self,
        parser_factory: ParserFactory,
        sub_checker: SubCheckerService
    ) -> BackgroundBuilder:
        return BackgroundBuilder(parser_factory=parser_factory, sub_checker=sub_checker)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder=builder)

    @singleton
    @provider
    def provide_bot(self, setting: Settings) -> BotManager:
        return BotManager(setting.BOT_TOKEN)
