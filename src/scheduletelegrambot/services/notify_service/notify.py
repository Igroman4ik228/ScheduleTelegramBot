from __future__ import annotations

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import html

from scheduletelegrambot.app.observer_pack.models import Observer
from scheduletelegrambot.bot.handlers.users.schedule import get_schedule
from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.database.repository import Repository
from scheduletelegrambot.services.formatter_service.schedule import (
    add_time_to_schedule,
)
from scheduletelegrambot.utils.constants import SENDER_TIME_SLEEP

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from scheduletelegrambot.database.db import DatabaseAlchemy
    from scheduletelegrambot.helpers.week import Week
    from scheduletelegrambot.services.sender_service.sender import SenderService


class NotifyService(Observer):
    def __init__(
        self,
        db: DatabaseAlchemy,
        sender: SenderService,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.sender = sender

    async def update(
        self,
        *,
        global_shift: int,
        week: Week,
    ) -> None:
        async with self.db.get_session() as session:
            await self._update(global_shift=global_shift, week=week, session=session)

    async def _update(
        self,
        *,
        global_shift: int,
        week: Week,
        session: AsyncSession,
    ) -> None:
        self.logger.info("Start NotifyService: global_shift=%s, week=%s", global_shift, week)

        repository = Repository(session)
        users = await repository.users.get_many(
            UserModel.is_notify.is_(True),
            UserModel.is_ban.is_(False),
            UserModel.is_bot.is_(False),
        )

        for user in users:
            if not self._should_notify(user, global_shift):
                continue
            if user.group_id is None:
                continue

            schedule = await get_schedule(user.group_id, repository, week.weekday, week.shift)

            formatted_schedule = self._format_message(schedule)
            await self.sender.safe_send_message(
                user.telegram_id, formatted_schedule, session=session
            )
            self.logger.info("Notify sent to %s", user)

        await asyncio.sleep(SENDER_TIME_SLEEP)

    def _should_notify(self, user: UserModel, global_shift: int) -> bool:
        if user.subscribe_id is None:
            return False
        return user.group is not None and user.group.global_shift == global_shift

    def _format_message(self, schedule: str) -> str:
        header = html.blockquote(html.bold("Уведомление"))
        schedule_with_time = add_time_to_schedule(schedule)
        return f"{header}\n{schedule_with_time}"
