from datetime import timedelta
from enum import Enum

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from injector import Module, provider, singleton
from redis.asyncio import Redis

from app.background_service_pack.builder import BackgroundBuilder
from app.background_service_pack.manager import BackgroundManager
from app.factory_pack.parser_factory import ParserFactory
from bot.bot import BotManager
from database.cache.base import BaseRedis, ICache
from database.cache.profile_cache import ProfileCache
from database.cache.repositories import CacheRepositoryService
from database.db import DatabaseAlchemy, IDatabase
from services.loader_service.default_schedule import DefaultScheduleLoader
from services.notify_service.notify import NotifyService
from services.parser_service.request import Request
from services.sender_service.sender import SenderService
from services.sub_checker_service.sub_checker import SubCheckerService
from utils.config import Settings
from utils.config import settings as global_settings

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
        return global_settings

    @singleton
    @provider
    def provide_db(self, settings: Settings) -> IDatabase:
        return DatabaseAlchemy(
            url=settings.db.url,
            echo=settings.db.echo,
            pool_pre_ping=settings.db.pre_ping,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
        )

    @singleton
    @provider
    def provide_bot(self, settings: Settings) -> Bot:
        return Bot(
            settings.bot.token, default=DefaultBotProperties(parse_mode="HTML")
        )

    @singleton
    @provider
    def provide_dispatcher(self, settings: Settings) -> Dispatcher:
        return Dispatcher(
            storage=RedisStorage.from_url(url=settings.redis.url(db=1))
        )

    @singleton
    @provider
    def provide_redis(self, settings: Settings) -> Redis:
        return Redis.from_url(settings.redis.url())

    @singleton
    @provider
    def provide_cache(self, redis: Redis) -> ICache:
        return BaseRedis(redis)

    @singleton
    @provider
    def provide_profile_cache(self, redis: Redis) -> ProfileCache:
        return ProfileCache(redis)

    @singleton
    @provider
    def provide_cache_service(self, cache: ICache) -> CacheRepositoryService:
        return CacheRepositoryService(cache)

    @singleton
    @provider
    def provide_sender_service(
        self, db: IDatabase, bot: Bot, cache_service: CacheRepositoryService
    ) -> SenderService:
        return SenderService(db, bot, cache_service)

    @singleton
    @provider
    def provide_bot_manager(
        self,
        bot: Bot,
        dp: Dispatcher,
        settings: Settings,
        db: IDatabase,
        sender_service: SenderService,
        profile_cache: ProfileCache,
        cache_service: CacheRepositoryService,
        parser_factory: ParserFactory,
    ) -> BotManager:
        return BotManager(
            bot,
            dp,
            settings,
            db,
            sender_service,
            profile_cache,
            cache_service,
            parser_factory,
        )

    @singleton
    @provider
    def provide_notify_service(
        self,
        db: IDatabase,
        sender: SenderService,
        cache_service: CacheRepositoryService,
    ) -> NotifyService:
        return NotifyService(db, sender, cache_service)

    @singleton
    @provider
    def provide_default_schedule_loader(
        self,
        db: IDatabase,
    ) -> DefaultScheduleLoader:
        return DefaultScheduleLoader(db)

    @singleton
    @provider
    def provide_request(
        self,
        settings: Settings,
        sender: SenderService,
    ) -> Request:
        return Request(settings.bot.admin_ids, sender)

    @singleton
    @provider
    def provide_parser_factory(
        self,
        request: Request,
        db: IDatabase,
        notify: NotifyService,
        cache_service: CacheRepositoryService,
    ) -> ParserFactory:
        factory = ParserFactory(
            TimeSpan.PARSER.value,
            SCHEDULE_URLS,
            request,
            db,
            notify,
            cache_service,
        )
        notify.set_parser_factory(factory)
        return factory

    @provider
    def provide_sub_checker_service(
        self, sender: SenderService
    ) -> SubCheckerService:
        return SubCheckerService(TimeSpan.SUB_CHECKER.value, sender)

    @provider
    def provide_builder(
        self, parser_factory: ParserFactory, sub_checker: SubCheckerService
    ) -> BackgroundBuilder:
        return BackgroundBuilder(parser_factory, sub_checker)

    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder)
