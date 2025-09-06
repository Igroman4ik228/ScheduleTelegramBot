from datetime import timedelta
from enum import Enum

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from injector import Module, provider, singleton

from app.background_service_pack.builder import BackgroundBuilder
from app.background_service_pack.manager import BackgroundManager
from app.factory_pack.parser_factory import ParserFactory
from bot.bot import BotManager
from services.notify_service.notify import NotifyService
from services.sender_service.sender import SenderService
from services.sub_checker_service.sub_checker import SubCheckerService
from utils.config import Settings

SCHEDULE_URLS = [
    "https://menu.sttec.yar.ru/timetable/rasp_first.html",
    "https://menu.sttec.yar.ru/timetable/rasp_second.html",
]


class TimeSpan(Enum):
    SUB_CHECKER = timedelta(minutes=10).seconds
    PARSER = timedelta(minutes=1).seconds


class AppModule(Module):
    @singleton
    @provider
    def provide_setting(self) -> Settings:
        return Settings()

    @singleton
    @provider
    def provide_bot(self, setting: Settings) -> Bot:
        return Bot(
            setting.bot.token, default=DefaultBotProperties(parse_mode="HTML")
        )

    @provider
    def provide_sender_service(self, bot: Bot) -> SenderService:
        return SenderService(bot)

    @singleton
    @provider
    def provide_parser_factory(
        self, notify: NotifyService, sender: SenderService
    ) -> ParserFactory:
        return ParserFactory(
            TimeSpan.PARSER.value, notify, SCHEDULE_URLS, sender
        )

    @provider
    def provide_sub_checker_service(
        self, sender: SenderService
    ) -> SubCheckerService:
        return SubCheckerService(TimeSpan.SUB_CHECKER.value, sender)

    @singleton
    @provider
    def provide_notify_service(self, sender: SenderService) -> NotifyService:
        return NotifyService(sender)

    @provider
    def provide_builder(
        self, parser_factory: ParserFactory, sub_checker: SubCheckerService
    ) -> BackgroundBuilder:
        return BackgroundBuilder(parser_factory, sub_checker)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder)

    @singleton
    @provider
    def provide_bot_manager(
        self,
        bot: Bot,
        parser_factory: ParserFactory,
    ) -> BotManager:
        return BotManager(
            bot,
            parser_factory,
        )
