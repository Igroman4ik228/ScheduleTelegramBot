from dataclasses import dataclass
from logging import Logger

from injector import inject

from BackgroundServicePack.models import BackgroundService
from NotifyService.notify import NotifyService
from ObserverPack.models import Publisher


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
        print(f"Parsing")
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
