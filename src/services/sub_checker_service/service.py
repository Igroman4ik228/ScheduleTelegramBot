
from app.background_service_pack.models import BackgroundService


class SubCheckerService(BackgroundService):
    def __init__(self, time_span: int):
        super().__init__(time_span)

    async def do_work(self):
        # ToDo: check user`s sub and edit data if sub is not active
        pass

    async def active(self):
        self.logger.info("SubCheckerSirvice active")
        await super().active()

    async def pause(self):
        self.logger.info("SubCheckerSirvice paused")
        await super().pause()

    async def stop(self):
        self.logger.info("SubCheckerSirvice stopped")
        await self.pause()
