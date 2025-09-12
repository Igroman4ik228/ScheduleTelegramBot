from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from injector import Injector, Module, provider, singleton
from redis.asyncio import Redis

from app.background_service_pack.builder import BackgroundBuilder
from app.background_service_pack.manager import BackgroundManager
from app.factory_pack.parser_factory import ParserFactory
from bot.bot import BotManager
from database.cache.base import BaseRedis, ICache
from database.cache.profile_cache import ProfileCache
from database.cache.repositories import CacheRepositoryService
from database.db import DatabaseAlchemy
from services.loader_service.default_schedule import DefaultScheduleLoader
from services.notify_service.notify import NotifyService
from services.request_service.request import RequestService
from services.sender_service.sender import SenderService
from services.sub_checker_service.sub_checker import SubCheckerService
from settings import Settings
from utils.constants import SCHEDULE_URLS, IntervalBgServices


def create_injector() -> Injector:
    return Injector(
        [
            ConfigModule(),
            DatabaseModule(),
            CacheModule(),
            BotModule(),
            ServiceModule(),
            BackgroundModule(),
        ]
    )


class ConfigModule(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return Settings()


class DatabaseModule(Module):
    @singleton
    @provider
    def provide_db(self, settings: Settings) -> DatabaseAlchemy:
        return DatabaseAlchemy(
            url=settings.db.url,
            echo=settings.db.echo,
            echo_pool=settings.db.echo,
            pool_pre_ping=settings.db.pre_ping,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
        )


class CacheModule(Module):
    @singleton
    @provider
    def provide_redis(self, settings: Settings) -> Redis:
        return Redis.from_url(settings.cache.url())

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


class BotModule(Module):
    @singleton
    @provider
    def provide_bot(self, settings: Settings) -> Bot:
        return Bot(
            settings.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode="HTML"),
        )

    @singleton
    @provider
    def provide_dispatcher(self, settings: Settings) -> Dispatcher:
        return Dispatcher(
            storage=RedisStorage.from_url(url=settings.cache.url(db=1))
        )

    @singleton
    @provider
    def provide_sender_service(
        self,
        db: DatabaseAlchemy,
        bot: Bot,
        cache_service: CacheRepositoryService,
    ) -> SenderService:
        return SenderService(db, bot, cache_service)

    @singleton
    @provider
    def provide_bot_manager(
        self,
        bot: Bot,
        dp: Dispatcher,
        settings: Settings,
        db: DatabaseAlchemy,
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


class ServiceModule(Module):
    @singleton
    @provider
    def provide_notify_service(
        self,
        db: DatabaseAlchemy,
        sender: SenderService,
        cache_service: CacheRepositoryService,
    ) -> NotifyService:
        return NotifyService(db, sender, cache_service)

    @singleton
    @provider
    def provide_default_schedule_loader(
        self,
        db: DatabaseAlchemy,
    ) -> DefaultScheduleLoader:
        return DefaultScheduleLoader(db)

    @singleton
    @provider
    def provide_request(
        self,
        settings: Settings,
        sender: SenderService,
    ) -> RequestService:
        return RequestService(settings.bot.admin_ids, sender)

    @singleton
    @provider
    def provide_parser_factory(
        self,
        request: RequestService,
        db: DatabaseAlchemy,
        notify: NotifyService,
        cache_service: CacheRepositoryService,
    ) -> ParserFactory:
        return ParserFactory(
            IntervalBgServices.PARSER.value,
            SCHEDULE_URLS,
            request,
            db,
            notify,
            cache_service,
        )

    @singleton
    @provider
    def provide_sub_checker_service(
        self, sender: SenderService
    ) -> SubCheckerService:
        return SubCheckerService(IntervalBgServices.SUB_CHECKER.value, sender)


class BackgroundModule(Module):
    @singleton
    @provider
    def provide_builder(
        self, parser_factory: ParserFactory, sub_checker: SubCheckerService
    ) -> BackgroundBuilder:
        return BackgroundBuilder(parser_factory, sub_checker)

    @singleton
    @provider
    def provide_manager(self, builder: BackgroundBuilder) -> BackgroundManager:
        return BackgroundManager(builder)
