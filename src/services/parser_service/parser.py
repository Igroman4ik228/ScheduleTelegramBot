from app.background_service_pack.models import (
    IntervalService,
)
from app.observer_pack.models import Publisher
from database.cache.repositories import CacheService
from database.db import DatabaseAlchemy, with_session
from database.repository import CachedRepository
from services.notify_service.notify import NotifyService
from services.parser_service.builder import Builder
from services.parser_service.html_parser import HtmlParser
from services.request_service.request import RequestService
from utils.constants import DEBUG


class ParserService(IntervalService, Publisher):
    def __init__(
        self,
        url: str,
        global_shift: int,
        interval: int,
        request: RequestService,
        db: DatabaseAlchemy,
        cache_service: CacheService,
        notify: NotifyService,
    ):
        IntervalService.__init__(self, interval)
        Publisher.__init__(self)

        self.parser: HtmlParser | None = None

        self.url = url
        self.global_shift = global_shift
        self.request = request
        self.db = db
        self.cache_service = cache_service

        self.attach(notify)

    async def do_work(self):
        response_text = await self._get_response_text()

        self.parser = HtmlParser(response_text)
        self.parser.initialize_week()

        replacement_schedules = self.parser.extract_replacement_schedules()

        builder = Builder(
            self.db, self.parser.week, self.global_shift, replacement_schedules
        )
        await builder.initialize()
        result_schedule = await builder.build()

        async with self.db.get_session() as session:
            repo = CachedRepository(session, self.cache_service)
            is_update = await self._check_changed_schedule(
                result_schedule, repo
            )

        if is_update:
            await self._save_schedule_to_db(result_schedule)
            await self.notify(
                global_shift=self.global_shift, week=self.parser.week
            )

    async def start(self):
        self.logger.info("ParserService active")
        await super().start()

    async def pause(self):
        self.logger.info("ParserService paused")
        await super().pause()

    async def stop(self):
        self.logger.info("ParserService stopped")
        super().stop()

    async def _get_response_text(self):
        if DEBUG:
            with open("test.html", "r", encoding="utf-8") as file:
                return file.read()
        return await self.request.fetch(self.url)

    @with_session
    async def _save_schedule_to_db(
        self, result_schedule: dict[str, str], session=None
    ):
        result_schedule_repo = CachedRepository(
            session, self.cache_service
        ).result_schedule

        for group, schedule in result_schedule.items():
            await result_schedule_repo.delete_by_group_name(
                self.parser.week.weekday, group
            )

            await result_schedule_repo.create_by_group_name(
                self.parser.week.weekday, schedule, group
            )

    async def _check_changed_schedule(
        self, result_schedule: dict[str, str], repo: CachedRepository
    ) -> bool:
        groups = await repo.groups.get_all_by_global_shift(self.global_shift)
        existing_schedules = (
            await repo.result_schedule.get_all_by_weekday_and_groups(
                self.parser.week.weekday, [g.id for g in groups]
            )
        )

        existing_dict = {sch.group_id: sch for sch in existing_schedules}
        groups_dict = {g.name: g for g in groups}

        for group_name, schedule in result_schedule.items():
            group = groups_dict.get(group_name)
            if not group:
                continue

            old_schedule = existing_dict.get(group.id)
            if old_schedule is None or old_schedule.data_lessons != schedule:
                return True
        return False
