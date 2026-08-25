from collections.abc import AsyncIterator  # noqa: TC003 - provider return type is runtime metadata.

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cashews import Cache  # noqa: TC002 - provider metadata is resolved by Dishka at runtime.
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import (
    AsyncSession,  # noqa: TC002 - provider return type is runtime metadata.
)

from scheduletelegrambot.app.application import Application
from scheduletelegrambot.app.factory_pack.parser_factory import (
    ParserFactory,
    ParserFactoryConfig,
)
from scheduletelegrambot.bot.bot import BotManager
from scheduletelegrambot.database.cache.cashews import cache
from scheduletelegrambot.database.cache.profile_cache import ProfileCache
from scheduletelegrambot.database.db import DatabaseAlchemy, EngineOptions
from scheduletelegrambot.database.repository import Repository
from scheduletelegrambot.services.loader_service.default_schedule import (
    DefaultScheduleLoader,
)
from scheduletelegrambot.services.notify_service.notify import NotifyService
from scheduletelegrambot.services.parser_service.parser import (
    ParserServiceDependencies,
)
from scheduletelegrambot.services.request_service.request import RequestService
from scheduletelegrambot.services.sender_service.sender import SenderService
from scheduletelegrambot.services.sub_checker_service.sub_checker import (
    SubCheckerService,
)
from scheduletelegrambot.settings import Settings
from scheduletelegrambot.utils.constants import SCHEDULE_URLS, IntervalBgServices


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def settings(self) -> Settings:
        return Settings()

    @provide
    async def database(self, settings: Settings) -> AsyncIterator[DatabaseAlchemy]:
        database = DatabaseAlchemy(
            url=settings.db.url,
            options=EngineOptions(
                echo=settings.db.echo,
                echo_pool=settings.db.echo,
                pool_pre_ping=settings.db.pre_ping,
                pool_size=settings.db.pool_size,
                max_overflow=settings.db.max_overflow,
            ),
        )
        try:
            yield database
        finally:
            await database.close()

    @provide
    async def cashews_cache(self, settings: Settings) -> AsyncIterator[Cache]:
        cache_url = settings.cache.url()
        cache.setup(cache_url, pickle_type="sqlalchemy")
        cache.setup_tags_backend(cache_url)
        await cache.init()
        try:
            yield cache
        finally:
            await cache.close()

    @provide
    def profile_cache(self, cashews_cache: Cache) -> ProfileCache:
        return ProfileCache(cashews_cache)

    @provide
    async def bot(self, settings: Settings) -> AsyncIterator[Bot]:
        bot = Bot(
            settings.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        try:
            yield bot
        finally:
            await bot.session.close()

    @provide
    async def dispatcher(self, settings: Settings) -> AsyncIterator[Dispatcher]:
        dispatcher = Dispatcher(storage=RedisStorage.from_url(settings.cache.url(db=1)))
        try:
            yield dispatcher
        finally:
            await dispatcher.storage.close()

    @provide
    def sender(self, db: DatabaseAlchemy, bot: Bot) -> SenderService:
        return SenderService(db, bot)

    @provide
    def notify(
        self,
        db: DatabaseAlchemy,
        sender: SenderService,
    ) -> NotifyService:
        return NotifyService(db, sender)

    @provide
    def request(self, settings: Settings, sender: SenderService) -> RequestService:
        return RequestService(settings.bot.admin_ids, sender)

    @provide
    def parser_factory(
        self,
        request: RequestService,
        db: DatabaseAlchemy,
        notify: NotifyService,
    ) -> ParserFactory:
        return ParserFactory(
            config=ParserFactoryConfig(
                interval=IntervalBgServices.PARSER.value,
                urls=SCHEDULE_URLS,
            ),
            dependencies=ParserServiceDependencies(
                request=request,
                db=db,
                notify=notify,
            ),
        )

    @provide
    def sub_checker(
        self,
        db: DatabaseAlchemy,
        sender: SenderService,
        cashews_cache: Cache,
    ) -> SubCheckerService:
        return SubCheckerService(db, sender, cashews_cache)

    @provide
    def scheduler(self) -> AsyncIOScheduler:
        return AsyncIOScheduler(job_defaults={"coalesce": True, "max_instances": 1})

    @provide
    def bot_manager(
        self, bot: Bot, dispatcher: Dispatcher, settings: Settings, cashews_cache: Cache
    ) -> BotManager:
        return BotManager(bot, dispatcher, settings, cashews_cache)

    @provide
    def default_schedule_loader(self, db: DatabaseAlchemy) -> DefaultScheduleLoader:
        return DefaultScheduleLoader(db)

    @provide
    def application(
        self,
        bot_manager: BotManager,
        scheduler: AsyncIOScheduler,
        parser_factory: ParserFactory,
        sub_checker: SubCheckerService,
        default_schedule_loader: DefaultScheduleLoader,
    ) -> Application:
        return Application(
            bot_manager=bot_manager,
            scheduler=scheduler,
            parser_factory=parser_factory,
            sub_checker=sub_checker,
            default_schedule_loader=default_schedule_loader,
        )


class RequestProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def session(
        self,
        db: DatabaseAlchemy,
    ) -> AsyncIterator[AsyncSession]:
        async with db.sessionmaker.begin() as session:
            yield session

    @provide
    def repository(
        self,
        session: AsyncSession,
    ) -> Repository:
        return Repository(session)


def create_container():
    return make_async_container(AppProvider(), RequestProvider(), AiogramProvider())
