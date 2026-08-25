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
    SubscribeService,
    UserService,
)
from scheduletelegrambot.settings import Settings
from scheduletelegrambot.utils.constants import SCHEDULE_URLS, BackgroundInterval


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
    def sender(self, db: DatabaseAlchemy, bot: Bot) -> TelegramSender:
        return TelegramSender(db, bot)

    @provide
    def notify(
        self,
        db: DatabaseAlchemy,
        sender: TelegramSender,
    ) -> ScheduleNotifier:
        return ScheduleNotifier(db, sender)

    @provide
    def request(self, settings: Settings, sender: TelegramSender) -> AdminRequester:
        return AdminRequester(settings.bot.admin_ids, sender)

    @provide
    def parser_factory(
        self,
        request: AdminRequester,
        db: DatabaseAlchemy,
        notify: ScheduleNotifier,
    ) -> ParserFactory:
        return ParserFactory(
            config=ParserFactoryConfig(
                interval=BackgroundInterval.PARSER.value,
                urls=SCHEDULE_URLS,
            ),
            dependencies=ParserDependencies(
                request=request,
                db=db,
                notify=notify,
            ),
        )

    @provide
    def sub_checker(
        self,
        db: DatabaseAlchemy,
        sender: TelegramSender,
        cashews_cache: Cache,
    ) -> SubscriptionChecker:
        return SubscriptionChecker(db, sender, cashews_cache)

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
        sub_checker: SubscriptionChecker,
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
    def department_service(self, session: AsyncSession) -> DepartmentService:
        return DepartmentService(DepartmentRepository(session))

    @provide
    def group_service(self, session: AsyncSession) -> GroupService:
        return GroupService(GroupRepository(session))

    @provide
    def default_schedule_service(self, session: AsyncSession) -> DefaultScheduleService:
        return DefaultScheduleService(DefaultScheduleRepository(session), GroupRepository(session))

    @provide
    def subscribe_service(self, session: AsyncSession) -> SubscribeService:
        return SubscribeService(SubscribeRepository(session))

    @provide
    def referral_service(self, session: AsyncSession) -> ReferralService:
        return ReferralService(ReferralRepository(session))

    @provide
    def user_service(self, session: AsyncSession) -> UserService:
        return UserService(UserRepository(session))

    @provide
    def result_schedule_service(self, session: AsyncSession) -> ResultScheduleService:
        return ResultScheduleService(ResultScheduleRepository(session), GroupRepository(session))


def create_container():
    return make_async_container(AppProvider(), RequestProvider(), AiogramProvider())
