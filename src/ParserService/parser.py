from datetime import time as dt_time
from logging import Logger

from bs4 import BeautifulSoup
from injector import inject

import constants
from BackgroundServicePack.models import BackgroundService
from NotifyService.notify import NotifyService
from ObserverPack.models import Publisher
from ParserService.builder import Builder
from ParserService.element_finder import ElementFinder
from ParserService.lesson import Lesson
from ParserService.request import Request
from ParserService.week import Week


class ParserService(BackgroundService, Publisher):
    @inject
    def __init__(self, url: str, time_span: int, logger: Logger, notify: NotifyService):
        BackgroundService.__init__(self, time_span, logger)
        Publisher.__init__(self, logger)

        self.request = Request(url, logger)

        self.attach(notify)

    async def do_work(self):
        response_text = await self.request.fetch()
        # with open('test.html', 'r', encoding='utf-8') as file:
        #     response_text = file.read()
        soup = BeautifulSoup(response_text, 'lxml')
        finder = ElementFinder(soup)

        week = Week(finder)
        self.logger.info(f"weekday: {week.weekday}, shift: {week.shift}")

        replacement_schedule = self._extract_replacement_schedule(finder.rows)

        builder = Builder(week.weekday, week.shift)
        result_schedule = builder.apply_replacement(replacement_schedule)
        result_schedule_str = builder.build_result_schedule(result_schedule)

        await builder.save_schedule_to_db(result_schedule_str)

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

            replacement_lesson = self._parse_replacement_lesson(cells)

            replacement_schedule.setdefault(group, [])
            replacement_schedule[group].append(replacement_lesson)

        return replacement_schedule

    def _parse_replacement_lesson(self, cells: BeautifulSoup) -> Lesson:
        lesson_numbers, time = self._get_lesson_numbers(
            cells[2].text.strip()
        )
        subject = cells[4].text.strip()
        classrooms = cells[5].text.strip()

        return Lesson(
            lesson_numbers,
            time,
            subject,
            classrooms,
            is_replacement=True)

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
        hours = int(hour_str)
        minutes = int(minute_str)

        time = (hours, minutes)
        lesson_number = Lesson.get_lesson_number_by_time(time)

        valid_time = dt_time(hours, minutes)
        return [lesson_number], valid_time

    def _parse_default_numbers(self) -> list[int]:
        """Возвращает все доступные номера уроков."""
        return list(range(len(constants.START_LESSONS_TIME)))
