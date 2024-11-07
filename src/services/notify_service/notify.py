import asyncio
from logging import getLogger

from app.observer_pack.models import Observer
from bot.bot import BotManager
from bot.handlers.users.schedule import process_schedule
from database.db import with_session_self
from database.models.users import UserModel
from database.repository import Repository
from services.parser_service.week import Week


class NotifyService(Observer):
    def __init__(self, bot_manager: BotManager):
        self.logger = getLogger(__class__.__name__)
        self.bot = bot_manager.bot

    @with_session_self
    async def update(self, session):
        self.logger.info("Start NotifyService")

        repo = Repository(session)
        users = await repo.users.get_all()
        for user in users:
            if self.need_notify(user):
                continue

            schedule_data = await repo.result_schedule.get(Week().weekday,
                                                           group_id=user.group_id)
            if schedule_data is None:
                continue

            await asyncio.sleep(0.05)
            formatted_schedule = process_schedule(user, schedule_data)
            try:
                await self.bot.send_message(user.telegram_id, formatted_schedule)
            except Exception:
                pass

    def need_notify(self, user: UserModel) -> bool:
        if not user.is_notify:
            return False

        if user.is_ban:
            return False

        if user.subscribe_id is None:
            return False

        return True
