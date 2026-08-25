from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX, cache
from scheduletelegrambot.database.repositories.users import UserRepository
from scheduletelegrambot.services.user import UserService
from scheduletelegrambot.utils.constants import BackgroundInterval

if TYPE_CHECKING:
    from cashews import Cache

    from scheduletelegrambot.components.sender.sender import TelegramSender
    from scheduletelegrambot.database.db import DatabaseAlchemy


class SubscriptionChecker:
    def __init__(
        self,
        db: DatabaseAlchemy,
        sender: TelegramSender,
        cashews_cache: Cache,
    ) -> None:
        self.interval = BackgroundInterval.SUB_CHECKER.value
        self.db = db
        self.sender = sender
        self.cache = cashews_cache

    async def do_work(self) -> None:
        today = datetime.now(UTC).date()
        async with self.db.get_session() as session:
            users = UserService(UserRepository(session))
            for user in await users.get_all_with_subscribe():
                subscribe = user.subscribe
                end_time = user.subscribe_end_time
                if subscribe is None or end_time is None:
                    continue
                days_left = (end_time.date() - today).days
                if days_left <= 0:
                    await users.update_subscribe(user, None, None)
                    await self._notify(user.telegram_id, TimeMessage.END, days_left)
                elif days_left in {1, 5, subscribe.duration_days // 2}:
                    message = {1: TimeMessage.ONE, 5: TimeMessage.FIVE}.get(
                        days_left, TimeMessage.HALF
                    )
                    await self._notify(user.telegram_id, message, days_left)
            await session.commit()

    @cache.locked(
        ttl="10s",
        key=f"{CACHE_KEY_PREFIX}:subscription-notification-lock:{{telegram_id}}:{{days_left}}",
    )
    async def _notify(self, telegram_id: int, message: TimeMessage, days_left: int) -> None:
        key = f"{CACHE_KEY_PREFIX}:subscription-notification:{telegram_id}:{days_left}"
        if await self.cache.exists(key):
            return
        await self.sender.safe_send_message(telegram_id, message.value)
        await self.cache.set(key, value=True, expire="1d")


class TimeMessage(Enum):
    END = (
        "Hi, дорогой пользователь!\n"
        "Срок действия твоей подписки закончился. 😥\n"
        "Оформить новую подписку можно прямо в боте. 🤩\n"
        "#ЭтоТебеНужно"
    )
    HALF = "Hi, дорогой пользователь!\nПрошла уже половина срока подписки. 🤓\n#ВремяЛетит"
    FIVE = (
        "Hi, дорогой пользователь!\n"
        "Срок действия твоей подписки закончится через 5 дней.\n"
        "#ЭтоПросто"
    )
    ONE = (
        "Hi, дорогой пользователь!\nСрок действия твоей подписки закончится уже завтра.\n#ЭтоУдобно"
    )
