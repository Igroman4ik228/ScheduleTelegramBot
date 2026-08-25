import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scheduletelegrambot.app.observer_pack.models import Publisher
from scheduletelegrambot.database.db import DatabaseAlchemy, with_session
from scheduletelegrambot.database.repository import Repository
from scheduletelegrambot.services.parser_service.builder import Builder
from scheduletelegrambot.services.parser_service.html_parser import HtmlParser
from scheduletelegrambot.utils.constants import DEBUG

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from scheduletelegrambot.services.notify_service.notify import NotifyService
    from scheduletelegrambot.services.request_service.request import RequestService


@dataclass(frozen=True)
class ParserServiceDependencies:
    request: RequestService
    db: DatabaseAlchemy
    notify: NotifyService


class ParserService(Publisher):
    def __init__(
        self,
        *,
        url: str,
        global_shift: int,
        interval: int,
        dependencies: ParserServiceDependencies,
    ):
        Publisher.__init__(self)

        self.parser: HtmlParser | None = None

        self.url = url
        self.global_shift = global_shift
        self.interval = interval
        self.request = dependencies.request
        self.db = dependencies.db

        self.attach(dependencies.notify)

    async def do_work(self) -> None:
        response_text = await self._get_response_text()

        self.parser = HtmlParser(response_text)
        self.parser.initialize_week()
        week = self.parser.week
        if week is None:
            raise RuntimeError("Parser did not initialize the schedule week")

        replacement_schedules = self.parser.extract_replacement_schedules()

        builder = Builder(self.db, week, self.global_shift, replacement_schedules)
        await builder.initialize()
        result_schedule = await builder.build()

        is_update = False
        async with self.db.get_session() as session:
            repository = Repository(session)

            for group, schedule in result_schedule.items():
                if await self._check_changed_schedule(group, schedule, repository):
                    is_update = True
                    break

        if is_update:
            await self._save_schedule_to_db(result_schedule)
            await self.notify(global_shift=self.global_shift, week=week)

    async def _get_response_text(self) -> str:
        if DEBUG:
            return await asyncio.to_thread(Path("test.html").read_text, encoding="utf-8")
        return await self.request.fetch(self.url)

    @with_session
    async def _save_schedule_to_db(
        self, result_schedule: dict[str, str], session: AsyncSession
    ) -> None:
        result_schedule_repo = Repository(session).result_schedule

        if self.parser is None or self.parser.week is None:
            raise RuntimeError("Schedule parser is not initialized")
        week = self.parser.week
        for group, schedule in result_schedule.items():
            await result_schedule_repo.upsert_by_group_name(week.weekday, schedule, group)

    async def _check_changed_schedule(
        self,
        group_name: str,
        current_result_schedule: str,
        repository: Repository,
    ) -> bool:
        group = await repository.groups.get_by_name(group_name)
        if group is None:
            return False

        if group.global_shift != self.global_shift:
            return False
        if self.parser is None or self.parser.week is None:
            raise RuntimeError("Schedule parser is not initialized")

        result_schedule = await repository.result_schedule.get(self.parser.week.weekday, group.id)

        return bool(
            result_schedule is None or result_schedule.data_lessons != current_result_schedule
        )
