import asyncio
from dataclasses import dataclass
from logging import Logger

from aiohttp import ClientError, ClientResponseError, ClientSession
from bs4 import BeautifulSoup
from injector import inject

from BackgroundServicePack.models import BackgroundService
from NotifyService.notify import NotifyService
from ObserverPack.models import Publisher

lesson: dict[int, str | None]


@dataclass
class Week():
    week_day: int
    week_schedule: int


class ParserService(BackgroundService, Publisher):
    @inject
    def __init__(self, time_span: int, logger: Logger, notify: NotifyService):
        BackgroundService.__init__(self, time_span, logger)
        Publisher.__init__(self, logger)

        self.attach(notify)

    async def do_work(self):
        # https://menu.sttec.yar.ru/timetable/rasp_first.html
        response_text = await self._fetch_schedule("https://menu.sttec.yar.ru/timetable/rasp_second.html")
        soup = BeautifulSoup(response_text, 'lxml')

        rows = self._get_rows(soup)

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

    def retry_request(self, func):
        async def wrapper(*args, **kwargs):
            for seconds in [15, 30, 60]:
                try:
                    return await func(*args, **kwargs)
                except ClientResponseError:
                    self.logger.error("Не удалось подключиться к сайту. "
                                      f"Повторная попытка через {seconds} секунд.")
                    await asyncio.sleep(seconds)
                except ClientError:
                    self.logger.error("Не удалось подключиться к сайту. "
                                      f"Повторная попытка через {seconds} секунд.")
                    await asyncio.sleep(seconds)
            return await func(*args, **kwargs)
        return wrapper

    @retry_request
    async def _fetch_schedule(self, url: str) -> str:
        async with ClientSession() as session:
            async with session.get(url, timeout=20) as response:
                response.raise_for_status()
                return await response.text()

    def _get_rows(self, soup: BeautifulSoup) -> list:
        table_data = soup.find('table')
        if table_data is None:
            raise ValueError("Таблица отсутствует.")

        rows = table_data.find_all('tr')[1:]  # Skip the header row
        return rows
