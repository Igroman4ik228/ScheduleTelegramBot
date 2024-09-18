import asyncio
from dataclasses import dataclass
from logging import Logger

from aiohttp import ClientError, ClientResponseError, ClientSession
from bs4 import BeautifulSoup
from injector import inject

import constants
from BackgroundServicePack.models import BackgroundService
from NotifyService.notify import NotifyService
from ObserverPack.models import Publisher
from ParserService.element_finder import ElementFinder
from ParserService.lesson import Lesson


@dataclass
class Week():
    weekday: int
    shift: int


def retry_request(func):
    async def wrapper(*args, **kwargs):
        for seconds in [15, 30, 60]:
            try:
                return await func(*args, **kwargs)
            except ClientResponseError:
                # self.logger.error("Не удалось подключиться к сайту. "
                #                   f"Повторная попытка через {seconds} секунд.")
                await asyncio.sleep(seconds)
            except ClientError:
                # self.logger.error("Не удалось подключиться к сайту. "
                #                   f"Повторная попытка через {seconds} секунд.")
                await asyncio.sleep(seconds)
        return await func(*args, **kwargs)
    return wrapper


class ParserService(BackgroundService, Publisher):
    @inject
    def __init__(self, time_span: int, logger: Logger, notify: NotifyService):
        BackgroundService.__init__(self, time_span, logger)
        Publisher.__init__(self, logger)

        self.attach(notify)

    async def do_work(self):
        # https://menu.sttec.yar.ru/timetable/rasp_first.html
        url = "https://menu.sttec.yar.ru/timetable/rasp_second.html"
        response_text = await self._fetch_schedule(url)
        soup = BeautifulSoup(response_text, 'lxml')
        finder = ElementFinder(soup)

        weekday = finder.get_weekday()
        shift = finder.get_shift()
        week = Week(weekday, shift)
        self.logger.info(f"weekday: {week.weekday}, shift: {week.shift}")

        replacement_lessons = self._parse_replacement_lessons(finder.rows)
        for replacement_lesson in replacement_lessons:
            self.logger.info(replacement_lesson)

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

    @retry_request
    async def _fetch_schedule(self, url: str) -> str:
        async with ClientSession() as session:
            async with session.get(url, timeout=20) as response:
                response.raise_for_status()
                return await response.text()

    def _parse_replacement_lessons(self, rows: BeautifulSoup) -> list[Lesson]:
        replacement_lessons = []
        for row in rows:
            cells = ElementFinder.get_cells(row)
            replacement_lesson = self._parse_replacement_lesson(cells)
            if replacement_lesson is None:
                continue

            replacement_lessons.append(replacement_lesson)
        return replacement_lessons

    def _parse_replacement_lesson(self, cells: BeautifulSoup) -> Lesson | None:
        group = cells[1].text.strip().upper()
        if group == '':
            return None

        lesson_numbers, time = self._parse_lesson_numbers(
            cells[2].text.strip()
        )

        subject = cells[4].text.strip()
        classrooms = cells[5].text.strip()

        return Lesson(group, lesson_numbers, time, subject, classrooms, is_replacement=True)

    def _parse_lesson_numbers(self, lesson_numbers_str: str):
        valid_numbers = []
        time = None

        if ',' in lesson_numbers_str:
            splited_numbers = lesson_numbers_str.split(',')
            for number in splited_numbers:
                valid_numbers.append(int(number))

        elif '-' in lesson_numbers_str:
            splited_numbers = lesson_numbers_str.split('-')
            start = int(splited_numbers[0])
            end = int(splited_numbers[-1])
            valid_numbers.extend(range(start, end + 1))

        elif lesson_numbers_str.count('.') == 1:
            splited_numbers = lesson_numbers_str.split('.')
            time = (int(splited_numbers[0]), int(splited_numbers[1]))
            valid_numbers.append(Lesson.get_lesson_number_by_time(time))

        elif lesson_numbers_str.isdigit():
            valid_numbers.append(int(lesson_numbers_str))

        elif lesson_numbers_str == "":
            for i in range(0, len(constants.START_LESSONS_TIME)):
                valid_numbers.append(i)

        else:
            raise ValueError("Неправильный формат номера замены: "
                             f"{lesson_numbers_str}")

        return valid_numbers, time
