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

        is_update = False
        async with self.db.get_session() as session:
            repository = CachedRepository(session, self.cache_service)

            for group, schedule in result_schedule.items():
                if await self._check_changed_schedule(
                    group, schedule, repository
                ):
                    is_update = True
                    break

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
        self,
        group_name: str,
        current_result_schedule: str,
        repository: CachedRepository,
    ) -> bool:
        group = await repository.groups.get_by_name(group_name)
        if group is None:
            return False

        if group.global_shift != self.global_shift:
            return False

        result_schedule = await repository.result_schedule.get(
            self.parser.week.weekday, group.id
        )

        if (
            result_schedule is None
            or result_schedule.data_lessons != current_result_schedule
        ):
            return True

        return False
