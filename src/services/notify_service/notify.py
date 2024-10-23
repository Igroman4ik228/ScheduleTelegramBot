import asyncio
from logging import getLogger

from bot.bot import BotManager
from bot.handlers.users.schedule import process_schedule
from database.db import with_session_self
from database.repository import Repository
from observer_pack.models import Observer
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
            if user.is_ban or not user.is_notify:
                continue
            if user.subscribe_id is None:
                continue
            result_schedule_data = await repo.result_schedule.get(Week().weekday,
                                                                  group_id=user.group_id)
            if result_schedule_data is None:
                continue

            await asyncio.sleep(0.05)
            result_schedule = process_schedule(user, result_schedule_data)
            try:
                await self.bot.send_message(user.telegram_id, result_schedule)
            except Exception:
                pass
