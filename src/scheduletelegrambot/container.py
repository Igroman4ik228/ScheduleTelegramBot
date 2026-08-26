from collections.abc import AsyncIterator

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.app.application import Application
from scheduletelegrambot.app.factory_pack.parser_factory import (
    ParserFactory,
    ParserFactoryConfig,
)
from scheduletelegrambot.bot.bot import BotManager
from scheduletelegrambot.components.loaders.default_schedule import (
    DefaultScheduleLoader,
)
from scheduletelegrambot.components.notifier.notify import ScheduleNotifier
from scheduletelegrambot.components.parsers.parser import (
    ParserDependencies,
)
from scheduletelegrambot.components.requester.request import AdminRequester
from scheduletelegrambot.components.sender.sender import TelegramSender
from scheduletelegrambot.components.subscription_checker.sub_checker import (
    SubscriptionChecker,
)
from scheduletelegrambot.database.cache.cashews import cache
from scheduletelegrambot.database.cache.profile_cache import ProfileCache
from scheduletelegrambot.database.db import DatabaseAlchemy, EngineOptions
from scheduletelegrambot.database.repositories.default_schedule import DefaultScheduleRepository
from scheduletelegrambot.database.repositories.departments import DepartmentRepository
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.database.repositories.referrals import ReferralRepository
from scheduletelegrambot.database.repositories.result_schedule import ResultScheduleRepository
from scheduletelegrambot.database.repositories.subscribes import SubscribeRepository
from scheduletelegrambot.database.repositories.users import UserRepository
from scheduletelegrambot.services import (
    DefaultScheduleService,
    DepartmentService,
    GroupService,
    ReferralService,
    ResultScheduleService,
    ScheduleService,
    SubscribeService,
    UserService,
)
from scheduletelegrambot.settings import Settings
from scheduletelegrambot.utils.constants import SCHEDULE_URLS, BackgroundInterval


class AppProvider(Provider):
    scope = Scope.APP

    components = provide_all(
        ProfileCache,
        TelegramSender,
        ScheduleNotifier,
        SubscriptionChecker,
        DefaultScheduleLoader,
        BotManager,
    )

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
    def requester(self, settings: Settings, sender: TelegramSender) -> AdminRequester:
        return AdminRequester(settings.bot.admin_ids, sender)

    @provide
    def parser_factory(
        self,
        request: AdminRequester,
        container: AsyncContainer,
        notify: ScheduleNotifier,
    ) -> ParserFactory:
        return ParserFactory(
            config=ParserFactoryConfig(
                interval=BackgroundInterval.PARSER.value,
                urls=SCHEDULE_URLS,
            ),
            dependencies=ParserDependencies(
                request=request,
                container=container,
                notify=notify,
            ),
        )

    @provide
    def scheduler(self) -> AsyncIOScheduler:
        return AsyncIOScheduler(job_defaults={"coalesce": True, "max_instances": 1})

    @provide
    async def application(
        self,
        bot_manager: BotManager,
        scheduler: AsyncIOScheduler,
        parser_factory: ParserFactory,
        sub_checker: SubscriptionChecker,
        default_schedule_loader: DefaultScheduleLoader,
        settings: Settings,
    ) -> AsyncIterator[Application]:
        cache_url = settings.cache.url()
        # Cached service results are immutable DTO schemas.
        cache.setup(cache_url, pickle_type="sqlalchemy")
        cache.setup_tags_backend(cache_url)
        await cache.init()

        try:
            yield Application(
                bot_manager=bot_manager,
                scheduler=scheduler,
                parser_factory=parser_factory,
                sub_checker=sub_checker,
                default_schedule_loader=default_schedule_loader,
            )
        finally:
            await cache.close()


class RequestProvider(Provider):
    scope = Scope.REQUEST

    repositories = provide_all(
        DepartmentRepository,
        GroupRepository,
        DefaultScheduleRepository,
        SubscribeRepository,
        ReferralRepository,
        UserRepository,
        ResultScheduleRepository,
    )
    services = provide_all(
        DepartmentService,
        GroupService,
        DefaultScheduleService,
        SubscribeService,
        ReferralService,
        UserService,
        ResultScheduleService,
        ScheduleService,
    )

    @provide
    async def session(
        self,
        db: DatabaseAlchemy,
    ) -> AsyncIterator[AsyncSession]:
        async with db.sessionmaker.begin() as session:
            yield session


def create_container():
    return make_async_container(AppProvider(), RequestProvider())
