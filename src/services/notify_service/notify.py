from __future__ import annotations

from logging import getLogger

from aiogram import html

from app.observer_pack.models import Observer
from bot.handlers.users.schedule import get_schedule
from database.cache.repositories import CacheService
from database.db import DatabaseAlchemy
from database.models import UserModel
from database.repository import CachedRepository
from helpers.week import Week
from services.formatter_service.schedule import add_time_to_schedule
from services.sender_service.sender import SenderService


class NotifyService(Observer):
    def __init__(
        self,
        db: DatabaseAlchemy,
        sender: SenderService,
        cache_service: CacheService,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.sender = sender
        self.cache_service = cache_service

    async def update(self, *, global_shift: int, week: Week):
        self.logger.info(
            f"Start NotifyService: global_shift={global_shift}, week={week}"
        )
        async with self.db.get_session() as session:
            repository = CachedRepository(session, self.cache_service)
            users = await repository.users.get_all(
                "group", is_notify=True, is_ban=False, is_bot=False
            )
        filtered_users = [
            user for user in users if self._should_notify(user, global_shift)
        ]
        grouped_users: dict[int, list[UserModel]] = {}
        for user in filtered_users:
            grouped_users.setdefault(user.group_id, []).append(user)

        for group_id, group_users in grouped_users.items():
            async with self.db.get_session() as session:
                repository = CachedRepository(session, self.cache_service)
                schedule = await get_schedule(
                    group_id, repository, week.weekday, week.shift
                )
            formatted_schedule = self._format_message(schedule)

            # Отправка всем пользователям группы
            tg_ids = [user.telegram_id for user in group_users]
            await self.sender.safe_send_range(tg_ids, formatted_schedule)

            self.logger.debug(
                f"Notify sent to {len(group_users)} users in group {group_id}"
            )

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
