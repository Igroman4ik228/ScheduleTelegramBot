from datetime import UTC, datetime
from typing import Self

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

from scheduletelegrambot.bot import BotManager
from scheduletelegrambot.components.loaders import InitialDataLoader
from scheduletelegrambot.components.parsers.parser_factory import ParserFactory
from scheduletelegrambot.components.subscription_checker.sub_checker import SubscriptionChecker


class Application:
    def __init__(
        self,
        *,
        bot_manager: BotManager,
        scheduler: AsyncIOScheduler,
        parser_factory: ParserFactory,
        sub_checker: SubscriptionChecker,
        container: AsyncContainer,
    ) -> None:
        self.bot_manager = bot_manager
        self.scheduler = scheduler
        self.parser_factory = parser_factory
        self.sub_checker = sub_checker
        self.container = container
        self._configured = False

    def configure(self, container: AsyncContainer) -> None:
        if self._configured:
            return

        setup_dishka(container=container, router=self.bot_manager.dispatcher, auto_inject=True)

        self._configure_jobs()

        self._configured = True

    async def __aenter__(self) -> Self:
        async with self.container() as request_container:
            initial_data_loader = await request_container.get(InitialDataLoader)
            await initial_data_loader.load()

        self.scheduler.start()

        return self

    async def __aexit__(self, *_: object) -> None:
        self.stop()

    async def start(self) -> None:
        await self.bot_manager.start_polling()

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
