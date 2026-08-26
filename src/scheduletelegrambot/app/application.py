from datetime import UTC, datetime
from typing import TYPE_CHECKING, Self

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka.integrations.aiogram import setup_dishka

from scheduletelegrambot.app.factory_pack.parser_factory import ParserFactory
from scheduletelegrambot.bot.bot import BotManager
from scheduletelegrambot.components.loaders.default_schedule import DefaultScheduleLoader
from scheduletelegrambot.components.subscription_checker.sub_checker import SubscriptionChecker

if TYPE_CHECKING:
    from dishka import AsyncContainer


class Application:
    def __init__(
        self,
        *,
        bot_manager: BotManager,
        scheduler: AsyncIOScheduler,
        parser_factory: ParserFactory,
        sub_checker: SubscriptionChecker,
        default_schedule_loader: DefaultScheduleLoader,
    ) -> None:
        self.bot_manager = bot_manager
        self.scheduler = scheduler
        self.parser_factory = parser_factory
        self.sub_checker = sub_checker
        self.default_schedule_loader = default_schedule_loader
        self._configured = False

    def configure(self, container: AsyncContainer) -> None:
        if self._configured:
            return

        setup_dishka(container=container, router=self.bot_manager.dp, auto_inject=True)

        self.bot_manager.configure()
        self._configure_jobs()

        self._configured = True

    async def __aenter__(self) -> Self:
        self.scheduler.start()
        return self

    async def __aexit__(self, *_: object) -> None:
        self.stop()

    async def start(self) -> None:
        await self.bot_manager.start()

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def _configure_jobs(self) -> None:
        now = datetime.now(UTC)
        for parser in self.parser_factory.get():
            self.scheduler.add_job(
                parser.do_work,
                "interval",
                seconds=parser.interval,
                id=f"schedule-parser-{parser.global_shift}",
                next_run_time=now,
                replace_existing=True,
            )

        self.scheduler.add_job(
            self.sub_checker.do_work,
            "interval",
            seconds=self.sub_checker.interval,
            id="subscription-checker",
            next_run_time=now,
            replace_existing=True,
        )
