from dataclasses import dataclass
from logging import Logger

from injector import inject

from BackgroundService.models import BackgroundService


@dataclass
class Week():
    week_day: int
    week_schedule: int


class ParserService(BackgroundService):
    @inject
    def __init__(self, time_span: int, logger: Logger):
        super().__init__(time_span, logger)

    async def do_work(self):
        print(f"Parsing")

    async def active(self):
        self.logger.log("ParserService active")
        await super().active()

    async def pause(self):
        self.logger.log("ParserService paused")
        await super().pause()

    async def stop(self):
        self.logger.log("ParserService stopped")
        await self.pause()

    async def _osdaj(self):
        pass
