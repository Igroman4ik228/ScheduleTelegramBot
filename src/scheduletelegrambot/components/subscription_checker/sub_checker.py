from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from dishka import AsyncContainer

from scheduletelegrambot.cache.cashews import CACHE_KEY_PREFIX, cache
from scheduletelegrambot.components.sender.sender import TelegramSender
from scheduletelegrambot.services.user import UserService
from scheduletelegrambot.utils.constants import BackgroundInterval


class SubscriptionChecker:
    def __init__(
        self,
        container: AsyncContainer,
        sender: TelegramSender,
    ) -> None:
        self.interval = BackgroundInterval.SUB_CHECKER.value
        self.container = container
        self.sender = sender

    async def do_work(self) -> None:
        today = datetime.now(UTC).date()
        async with self.container() as request_container:
            users = await request_container.get(UserService)
            for user in await users.list_all_with_subscribe():
                subscribe = user.subscribe
                end_time = user.subscribe_end_time
                if subscribe is None or end_time is None:
                    continue
                days_left = (end_time.date() - today).days
                if days_left <= 0:
                    await users.update_subscribe(user.telegram_id, None, None)
                    await self._notify(user.telegram_id, TimeMessage.END, days_left)
                elif days_left in {1, 5, subscribe.duration_days // 2}:
                    message = {1: TimeMessage.ONE, 5: TimeMessage.FIVE}.get(
                        days_left, TimeMessage.HALF
                    )
                    await self._notify(user.telegram_id, message, days_left)

    @cache.locked(
        ttl="10s",
        key=f"{CACHE_KEY_PREFIX}:subscription-notification-lock:{{telegram_id}}:{{days_left}}",
    )
    async def _notify(self, telegram_id: int, message: TimeMessage, days_left: int) -> None:
        key = f"{CACHE_KEY_PREFIX}:subscription-notification:{telegram_id}:{days_left}"
        if await cache.exists(key):
            return
        await self.sender.safe_send_message(telegram_id, message.value)
        await cache.set(key, value=True, expire="1d")


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
