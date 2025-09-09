from __future__ import annotations

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import html

from app.observer_pack.models import Observer
from bot.handlers.users.schedule import get_schedule
from database.cache.repositories import CacheRepositoryService
from database.db import IDatabase, with_session
from database.models import UserModel
from database.models.groups import GroupModel
from database.repository import CachedRepository
from services.formatter_service.schedule import add_time_to_schedule
from services.sender_service.sender import SenderService
from utils.constants import SENDER_TIME_SLEEP

if TYPE_CHECKING:
    from app.factory_pack.parser_factory import ParserFactory


class NotifyService(Observer):
    def __init__(
        self,
        db: IDatabase,
        sender: SenderService,
        cache_service: CacheRepositoryService,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.sender = sender
        self.cache_service = cache_service
        self.parser_factory: ParserFactory | None = None

    def set_parser_factory(self, parser_factory: ParserFactory):
        self.parser_factory = parser_factory

    @with_session
    async def update(self, *args, session=None):
        self.logger.info("Start NotifyService")
        if self.parser_factory is None:
            return

        number_parser = args[0]

        repository = CachedRepository(session, self.cache_service)
        users = await repository.users.get_all("group")
        for user in users:
            if not self.need_notify(user):
                continue

            group: GroupModel = user.group
            if group.global_shift != number_parser:
                # этот пользователь другой смены → пропускаем
                continue

            week = self.parser_factory.get_week(group.global_shift)

            formatted_schedule = await get_schedule(
                user.group_id, repository, week.weekday, week.shift
            )

            formatted_schedule = add_time_to_schedule(formatted_schedule)

            header = html.blockquote(html.bold("Уведомление"))
            formatted_schedule = f"{header}\n{formatted_schedule}"

            await self.sender.safe_send_message(
                user.telegram_id, formatted_schedule, session=session
            )

        await asyncio.sleep(SENDER_TIME_SLEEP)

    def need_notify(self, user: UserModel) -> bool:
        return (
            user.is_notify and not user.is_ban and user.subscribe_id is not None
        )
