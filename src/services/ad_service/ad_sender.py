from injector import inject

from app.background_service_pack.models import BackgroundService


class AdService(BackgroundService):
    @inject
    def __init__(self, time_span: int):
        super().__init__(time_span)

    async def do_work(self):
        print(f"Ad Sending every {self.time_span} seconds")

    async def active(self):
        self.logger.info("AdService active")
        await super().active()

    async def pause(self):
        self.logger.info("AdService paused")
        await super().pause()

    async def stop(self):
        self.logger.info("AdService stopped")
        await self.pause()
