from logging import Logger

from injector import inject
from BackgroundService.models import BackgroundService


class AdService(BackgroundService):
    @inject
    def __init__(self, time_span: int, logger: Logger):
        super().__init__(time_span, logger)

    async def do_work(self):
        print(f"Ad Sending every {self.time_span} seconds")

    async def active(self):
        self.logger.log("AdService active")
        await super().active()

    async def pause(self):
        self.logger.log("AdService paused")
        await super().pause()

    async def stop(self):
        self.logger.log("AdService stopped")
        await self.pause()
