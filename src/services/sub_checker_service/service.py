
import datetime

from app.background_service_pack.models import BackgroundService
from database.db import sessionmaker, with_session_self
from database.repository import Repository


class SubCheckerService(BackgroundService):
    def __init__(self, time_span: int):
        super().__init__(time_span)

    @with_session_self
    async def do_work(self, session):
        user_repo = Repository(session).users
        users = await user_repo.get_all()

        for user in users:
            is_subscribe_active = check_subscribe(user.subscribe_end_time)
            if not is_subscribe_active:
                user.subscribe_id = None
                user.subscribe_end_time = None
                # todo Проверить
                user.subscribe = None

                await user_repo.update(user)

    async def active(self):
        self.logger.info("SubCheckerSirvice active")
        await super().active()

    async def pause(self):
        self.logger.info("SubCheckerSirvice paused")
        await super().pause()

    async def stop(self):
        self.logger.info("SubCheckerSirvice stopped")
        await self.pause()


def check_subscribe(subscribe_end_time: datetime) -> bool:
    if datetime.datetime.now() > subscribe_end_time:
        return False
    return True
