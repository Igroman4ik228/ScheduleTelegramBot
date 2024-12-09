from injector import inject

from app.background_service_pack.models import BackgroundService
from app.observer_pack.models import Publisher
from database.db import sessionmaker, with_session_self
from database.repository import Repository
from helpers.week import Week
from services.notify_service.notify import NotifyService
from services.parser_service.builder import Builder
from services.parser_service.html_parser import HtmlParser
from services.parser_service.request import Request
from utils.config import settings


class ParserService(BackgroundService, Publisher):
    @inject
    def __init__(self, url: str, time_span: int,  notify: NotifyService):
        BackgroundService.__init__(self, time_span)
        Publisher.__init__(self)

        self.request = Request(url)

        self.attach(notify)

    async def do_work(self):
        response_text = await self._get_response_text()

        parser = HtmlParser(response_text)
        parser.initialize_week()

        replacement_schedules = parser.extract_replacement_schedules()

        builder = Builder(replacement_schedules)
        builder.initialize()
        result_schedule = await builder.build()

        for group, schedule in result_schedule.items():
            if await self._check_changed_schedule(group, schedule):
                self.is_update = True
                break

        if self.is_update:
            await self._save_schedule_to_db(result_schedule)

        await self.notify()

    async def active(self):
        self.logger.info("ParserService active")
        await super().active()

    async def pause(self):
        self.logger.info("ParserService paused")
        await super().pause()

    async def stop(self):
        self.logger.info("ParserService stopped")
        await self.pause()

    async def _get_response_text(self):
        if settings.DEBUG:
            with open('test.html', 'r', encoding='utf-8') as file:
                return file.read()
        return await self.request.fetch()

    @with_session_self
    async def _save_schedule_to_db(self, session, result_schedule: dict[str, str]):
        result_schedule_rep = Repository(session).result_schedule

        for group, schedule in result_schedule.items():
            await result_schedule_rep.delete_by_group_name(Week().weekday, group)

            await result_schedule_rep.create_by_group_name(Week().weekday, schedule, group)

    async def _check_changed_schedule(self, group_name: str, current_result_schedule: str) -> bool:
        async with sessionmaker() as session:
            repo = Repository(session)
            group = await repo.groups.get_by_name(group_name)
            if group is None:
                return False

            result_schedule = await repo.result_schedule.get(Week().weekday,
                                                             group.id)

        if result_schedule is None or result_schedule.data_lessons != current_result_schedule:
            return True

        return False
