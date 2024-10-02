from datetime import time as dt_time
from logging import Logger

from bs4 import BeautifulSoup
from injector import inject

from background_service_pack.models import BackgroundService
from config import settings
from notify_service.notify import NotifyService
from observer_pack.models import Publisher
from parser_service.builder import Builder
from parser_service.element_finder import ElementFinder
from parser_service.lesson import Lesson
from parser_service.request import Request
from parser_service.week import Week
from utils import constants


class ParserService(BackgroundService, Publisher):
    @inject
    def __init__(self, url: str, time_span: int, logger: Logger, notify: NotifyService):
        BackgroundService.__init__(self, time_span, logger)
        Publisher.__init__(self, logger)

        self.request = Request(url, logger)

        self.attach(notify)

    async def do_work(self):
        if settings.DEBUG:
            with open('test.html', 'r', encoding='utf-8') as file:
                response_text = file.read()
        else:
            response_text = await self.request.fetch()

        soup = BeautifulSoup(response_text, 'lxml')
        finder = ElementFinder(soup)

        week = Week(finder)
        self.logger.info(f"weekday: {week.weekday}, shift: {week.shift}")

        replacement_schedule = self._extract_replacement_schedule(finder.rows)

        builder = Builder(week.weekday, week.shift)
        result_schedule_data = builder.apply_replacement(replacement_schedule)
        result_schedule = builder.build_result_schedule(result_schedule_data)

        await builder.save_schedule_to_db(result_schedule)

        self.is_update = True
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

    def _extract_replacement_schedule(self, rows: BeautifulSoup) -> dict[str, list[Lesson]]:
        replacement_schedule = {}
        for row in rows:
            cells = ElementFinder.get_cells(row)

            group = self._parse_group(cells)
            if group is None:
                continue

            replacement_lessons = self._parse_replacement_lessons(cells)

            replacement_schedule.setdefault(group, [])
            for replacement_lesson in replacement_lessons:
                replacement_schedule[group].append(replacement_lesson)

        return replacement_schedule

    def _parse_replacement_lessons(self, cells: BeautifulSoup) -> list[Lesson]:
        lesson_numbers, time = self._get_lesson_numbers(
            cells[2].text.strip()
        )
        subject = cells[4].text.strip()
        classrooms = cells[5].text.strip()

        replacement_lessons = []
        for lesson_number in lesson_numbers:
            replacement_lessons.append(
                Lesson(
                    lesson_number,
                    time,
                    subject,
                    classrooms,
                    is_replacement=True)
            )

        return replacement_lessons

    def _parse_group(self, cells: BeautifulSoup) -> str | None:
        group = cells[1].text.strip().upper()
        if group == '':
            return None
        return group

    def _get_lesson_numbers(self, lesson_numbers: str) -> tuple[list[int], dt_time | None]:
        if ',' in lesson_numbers:
            return self._parse_comma_separated(lesson_numbers), None

        if '-' in lesson_numbers:
            return self._parse_range(lesson_numbers), None

        if lesson_numbers.count('.') == 1:
            return self._parse_time_format(lesson_numbers)

        if lesson_numbers.isdigit():
            return [int(lesson_numbers)], None

        if lesson_numbers == "":
            return self._parse_default_numbers(), None

        raise ValueError("Неправильный формат номера замены: "
                         f"{lesson_numbers}")

    def _parse_range(self, lesson_numbers: str) -> list[int]:
        start, end = lesson_numbers.split('-')
        start = int(start)
        end = int(end)

        return list(range(start, end + 1))

    def _parse_comma_separated(self, lesson_numbers: str) -> list[int]:
        lesson_numbers = lesson_numbers.split(',')
        result_numbers = []
        for number in lesson_numbers:
            result_numbers.append(int(number.strip()))

        return result_numbers

    def _parse_time_format(self, lesson_numbers_string: str) -> tuple[list[int], dt_time]:
        """Парсит строку с указанием времени в формате 'час.минуты'."""
        hour_str, minute_str = lesson_numbers_string.split('.')
        hours, minutes = int(hour_str), int(minute_str)

        time = dt_time(hours, minutes)
        lesson_number = Lesson.get_lesson_number_by_time(time)

        return [lesson_number], time

    def _parse_default_numbers(self) -> list[int]:
        """Возвращает все доступные номера уроков."""
        return list(range(len(constants.START_LESSONS_TIME)))
