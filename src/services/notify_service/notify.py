import asyncio
from logging import getLogger

from bot.bot import BotManager
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

        users = await Repository(session).users.get_all()
        for user in users:
            result_schedule = await Repository(session).result_schedule.get(Week().weekday,
                                                                            group_id=user.group_id)
            await asyncio.sleep(0.05)
            if result_schedule is not None:
                if user.is_ban:
                    continue
                try:
                    await self.bot.send_message(user.telegram_id, result_schedule.data_lessons)
                except Exception:
                    pass
