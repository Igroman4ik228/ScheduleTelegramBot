from __future__ import annotations

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import html

from app.observer_pack.models import Observer
from bot.handlers.users.schedule import get_schedule
from database.db import DatabaseAlchemy, with_session
from database.models import UserModel
from database.repository import CachedRepository
from helpers.cache import CacheHelper
from helpers.week import Week
from services.formatter_service.schedule import add_time_to_schedule
from services.sender_service.sender import SenderService
from utils.constants import SENDER_TIME_SLEEP

if TYPE_CHECKING:
    pass


class NotifyService(Observer):
    def __init__(
        self,
        db: DatabaseAlchemy,
        sender: SenderService,
        cache_service: CacheHelper,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.sender = sender
        self.cache_service = cache_service

    @with_session
    async def update(self, *, global_shift: int, week: Week, session=None):
        self.logger.info(
            f"Start NotifyService: global_shift={global_shift}, week={week}"
        )

        repository = CachedRepository(session, self.cache_service)
        users = await repository.users.get_all(
            "group", is_notify=True, is_ban=False, is_bot=False
        )

        for user in users:
            if not self._should_notify(user, global_shift):
                continue

            schedule = await get_schedule(
                user.group_id, repository, week.weekday, week.shift
            )

            formatted_schedule = self._format_message(schedule)
            await self.sender.safe_send_message(
                user.telegram_id, formatted_schedule, session=session
            )
            self.logger.info(f"Notify sent to {user}")

        await asyncio.sleep(SENDER_TIME_SLEEP)

    def _should_notify(self, user: UserModel, global_shift: int) -> bool:
        if user.subscribe_id is None:
            return False
        if user.group.global_shift != global_shift:
            return False
        return True

    def _format_message(self, schedule: str) -> str:
        header = html.blockquote(html.bold("Уведомление"))
        schedule_with_time = add_time_to_schedule(schedule)
        return f"{header}\n{schedule_with_time}"
