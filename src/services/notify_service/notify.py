import asyncio
from logging import getLogger

from bot.bot import BotManager
from database.db import with_session_self
from database.repositories.result_schedule import ResultScheduleRepository
from database.repositories.users import UserRepository
from observer_pack.models import Observer
from services.parser_service.week import Week


class NotifyService(Observer):
    def __init__(self, bot_manager: BotManager):
        self.logger = getLogger(__class__.__name__)
        self.bot = bot_manager.bot

    @with_session_self
    async def update(self, session):
        self.logger.info("Start NotifyService")

        users = await UserRepository(session).get_all()
        for user in users:
            result_schedule = await ResultScheduleRepository(session).get(Week.weekday,
                                                                          group_id=user.group_id)
            await asyncio.sleep(0.1)
            if result_schedule is not None:
                await self.bot.send_message(user.telegram_id, result_schedule.data_lessons)
