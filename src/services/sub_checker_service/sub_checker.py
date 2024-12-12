
import datetime

from app.background_service_pack.models import BackgroundService
from database.db import sessionmaker, with_session_self
from database.repository import Repository


class SubCheckerService(BackgroundService):
    def __init__(self, time_span: int):
        super().__init__(time_span)

    async def do_work(self):
        # TODO
        pass

    async def active(self):
        self.logger.info("SubCheckerService active")
        await super().active()

    async def pause(self):
        self.logger.info("SubCheckerService paused")
        await super().pause()

    async def stop(self):
        self.logger.info("SubCheckerService stopped")
        await self.pause()
