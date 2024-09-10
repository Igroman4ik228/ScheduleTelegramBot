from logging import Logger

from injector import inject
from BackgroundService.models import BackgroundService


class ParserService(BackgroundService):
    @inject
    def __init__(self, time_span: int, logger: Logger):
        super().__init__(time_span, logger)

    async def do_work(self):
        print(f"Parsing for {self.path} for schedule data: {self.schedule_data}")

    async def active(self):
        self.logger.log("ParserService active")
        await super().active()

    async def pause(self):
        self.logger.log("ParserService paused")
        await super().pause()

    async def stop(self):
        self.logger.log("ParserService stopped")
        await self.pause()
