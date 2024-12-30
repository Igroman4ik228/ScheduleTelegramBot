import asyncio
from logging import getLogger

from app.observer_pack.models import Observer
from bot.handlers.users.schedule import get_schedule
from database.db import with_session_self
from database.models.users import UserModel
from database.repository import Repository
from helpers.week import Week
from services.sender_service.sender import SenderService
from utils.constants import SENDER_TIME_SLEEP


class NotifyService(Observer):

    def __init__(self, sender: SenderService):
        self.logger = getLogger(self.__class__.__name__)
        self.sender = sender

    @with_session_self
    async def update(self, session):
        self.logger.info("Start NotifyService")

        repo = Repository(session)
        users = await repo.users.get_all()
        for user in users:
            if self.need_notify(user):
                continue

            formatted_schedule = await get_schedule(
                user.group_id, repo,
                Week().weekday, Week().shift
            )
            await self.sender.safe_send_message(user.telegram_id, formatted_schedule)

            await asyncio.sleep(SENDER_TIME_SLEEP)

    def need_notify(self, user: UserModel) -> bool:
        if not user.is_notify:
            return False

        if user.is_ban:
            return False

        if user.subscribe_id is None:
            return False

        return True
