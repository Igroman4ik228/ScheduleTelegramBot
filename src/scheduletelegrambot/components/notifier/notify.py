from __future__ import annotations

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import html
from dishka import AsyncContainer

from scheduletelegrambot.app.observer_pack.models import Observer
from scheduletelegrambot.components.formatters.schedule import add_time_to_schedule
from scheduletelegrambot.components.sender.sender import TelegramSender
from scheduletelegrambot.schemas.user import UserWithGroupSchema
from scheduletelegrambot.services.schedule import ScheduleService
from scheduletelegrambot.services.user import UserService
from scheduletelegrambot.utils.constants import SENDER_TIME_SLEEP

if TYPE_CHECKING:
    from scheduletelegrambot.helpers.week import Week


class ScheduleNotifier(Observer):
    def __init__(
        self,
        container: AsyncContainer,
        sender: TelegramSender,
    ) -> None:
        self.logger = getLogger(self.__class__.__name__)
        self.container = container
        self.sender = sender

    async def update(
        self,
        *,
        global_shift: int,
        week: Week,
    ) -> None:
        async with self.container() as request_container:
            users = await request_container.get(UserService)
            schedules = await request_container.get(ScheduleService)
            await self._update(
                global_shift=global_shift,
                week=week,
                users=users,
                schedules=schedules,
            )

    async def _update(
        self,
        *,
        global_shift: int,
        week: Week,
        users: UserService,
        schedules: ScheduleService,
    ) -> None:
        self.logger.info("Start ScheduleNotifier: global_shift=%s, week=%s", global_shift, week)

        notification_recipients = await users.list_notification_recipients()

        for user in notification_recipients:
            if not self._should_notify(user, global_shift):
                continue
            if user.group_id is None:
                continue

            schedule = await schedules.get(user.group_id, week.weekday, week.shift)

            formatted_schedule = self._format_message(schedule)
            await self.sender.safe_send_message(user.telegram_id, formatted_schedule)
            self.logger.info("Notify sent to %s", user)

        await asyncio.sleep(SENDER_TIME_SLEEP)

    def _should_notify(self, user: UserWithGroupSchema, global_shift: int) -> bool:
        if user.subscribe_id is None:
            return False
        return user.group is not None and user.group.global_shift == global_shift

    def _format_message(self, schedule: str) -> str:
        header = html.blockquote(html.bold("Уведомление"))
        schedule_with_time = add_time_to_schedule(schedule)
        return f"{header}\n{schedule_with_time}"
