from datetime import datetime, timedelta
from logging import getLogger

from app.background_service_pack.models import BackgroundService
from database.db import sessionmaker, with_session_self
from database.models.subscribe import SubscribeModel
from database.repository import Repository


class SubCheckerService(BackgroundService):
    def __init__(self, time_span: int):
        super().__init__(time_span)

    async def do_work(self):
        # Todo:
        async with sessionmaker() as session:
            repo = Repository(session)
            users = await repo.users.get_all()

        for user in users:
            user_sub: SubscribeModel = user.subscribe
            current_time = datetime.now().date()
            subscribe_end_time = user.subscribe_end_time.date()
            sub_half_time_span = user_sub.duration_days / 2

            # Check 5 days before end sub
            if subscribe_end_time - current_time == timedelta(days=5):
                pass

            # Check 1 day before end sub
            if subscribe_end_time - current_time == timedelta(days=1):
                pass

            # Check half time of end sub
            if subscribe_end_time - current_time == timedelta(days=sub_half_time_span):
                pass

            # Check end time of sub
            if subscribe_end_time <= current_time:
                await self._del_sub(user.telegram_id)

    async def _del_sub(self, user_tg_id):
        async with sessionmaker() as session:
            repo = Repository(session)
            user = await repo.users.get(user_tg_id)

            user.subscribe_end_time = None
            user.subscribe_id = None

            await repo.users.update(user)

    async def active(self):
        self.logger.info("SubCheckerService active")
        await super().active()

    async def pause(self):
        self.logger.info("SubCheckerService paused")
        await super().pause()

    async def stop(self):
        self.logger.info("SubCheckerService stopped")
        await self.pause()
