import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scheduletelegrambot.app.observer_pack.models import Publisher
from scheduletelegrambot.components.parsers.builder import Builder
from scheduletelegrambot.components.parsers.html_parser import HtmlParser
from scheduletelegrambot.database.db import DatabaseAlchemy, with_session
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.database.repositories.result_schedule import ResultScheduleRepository
from scheduletelegrambot.services.group import GroupService
from scheduletelegrambot.services.result_schedule import ResultScheduleService
from scheduletelegrambot.utils.constants import DEBUG

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from scheduletelegrambot.components.notifier.notify import ScheduleNotifier
    from scheduletelegrambot.components.requester.request import AdminRequester


@dataclass(frozen=True)
class ParserDependencies:
    request: AdminRequester
    db: DatabaseAlchemy
    notify: ScheduleNotifier


class ScheduleParser(Publisher):
    def __init__(
        self,
        *,
        url: str,
        global_shift: int,
        interval: int,
        dependencies: ParserDependencies,
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
            groups = GroupService(GroupRepository(session))
            result_schedules = ResultScheduleService(
                ResultScheduleRepository(session), GroupRepository(session)
            )

            for group, schedule in result_schedule.items():
                if await self._check_changed_schedule(group, schedule, groups, result_schedules):
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
        result_schedules = ResultScheduleService(
            ResultScheduleRepository(session), GroupRepository(session)
        )

        if self.parser is None or self.parser.week is None:
            raise RuntimeError("Schedule parser is not initialized")
        week = self.parser.week
        for group, schedule in result_schedule.items():
            await result_schedules.upsert_by_group_name(week.weekday, schedule, group)

    async def _check_changed_schedule(
        self,
        group_name: str,
        current_result_schedule: str,
        groups: GroupService,
        result_schedules: ResultScheduleService,
    ) -> bool:
        group = await groups.get_by_name(group_name)
        if group is None:
            return False

        if group.global_shift != self.global_shift:
            return False
        if self.parser is None or self.parser.week is None:
            raise RuntimeError("Schedule parser is not initialized")

        result_schedule = await result_schedules.get(self.parser.week.weekday, group.id)

        return bool(
            result_schedule is None or result_schedule.data_lessons != current_result_schedule
        )
