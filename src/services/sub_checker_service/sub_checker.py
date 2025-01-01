from datetime import datetime, timedelta
from enum import Enum

from app.background_service_pack.models import BackgroundService
from database.db import db_helper
from database.models.subscribe import SubscribeModel
from database.redis.service_cache import ServiceCache
from database.repository import Repository
from services.sender_service.sender import SenderService


class SubCheckerService(BackgroundService):

    def __init__(self, time_span: int, sender: SenderService):
        super().__init__(time_span)

        self.sender = sender
        self._service_cache = ServiceCache(self)

    async def do_work(self):
        async with db_helper.get_session() as session:
            repo = Repository(session)
            users = await repo.users.get_all("subscribe")

        for user in users:
            if await self._service_cache.get(user.telegram_id) == "true":
                continue

            user_sub: SubscribeModel = user.subscribe
            current_time = datetime.now().date()

            if user.subscribe_end_time == None:
                continue

            subscribe_end_time = user.subscribe_end_time.date()
            sub_half_time_span = int(user_sub.duration_days / 2)

            # Check 1 day before end sub
            if subscribe_end_time - current_time == timedelta(days=1):
                await self.sender.safe_send_message(user.telegram_id, TimeMessage.ONE.value)

            # Check 5 days before end sub
            elif subscribe_end_time - current_time == timedelta(days=5):
                await self.sender.safe_send_message(user.telegram_id, TimeMessage.FIVE.value)

            # Check half time of end sub
            elif subscribe_end_time - current_time == timedelta(days=sub_half_time_span):
                await self.sender.safe_send_message(user.telegram_id, TimeMessage.HALF.value)

            # Check end time of sub
            elif subscribe_end_time <= current_time:
                await self._del_sub(user.telegram_id)
                self.logger.info(f"Subscribe: {user.subscribe.id} del for user: {
                                 user.telegram_id}")
                await self.sender.safe_send_message(user.telegram_id, TimeMessage.END.value)

            await self._service_cache.create(user.telegram_id, "true")

    async def _del_sub(self, user_tg_id):
        async with db_helper.get_session() as session:
            repo = Repository(session)
            user = await repo.users.get(user_tg_id)

            user.subscribe_end_time = None
            user.subscribe_id = None

            await repo.users.update(user)

    async def active(self):
        self.logger.info("SubCheckerService active")
        await super().active()

    async def pause(self):
        self.logger.info("SubCheckerService paused")
        await super().pause()

    async def stop(self):
        self.logger.info("SubCheckerService stopped")
        await self.pause()


class TimeMessage(Enum):
    END = "Hi, дорогой пользователь!\n" \
        "У меня для тебя плохая новость. Срок действия твоей подписки закончился. 😥\n" \
        "Но не стоит унывать, ты всегда можешь оформить её прямо тут! 🤩\n" \
        "#ЭтоТебеНужно"
    HALF = "Hi, дорогой пользователь!\n" \
        "Ну, как? Нравится? Удобно? Практично?\n" \
        "Конечно да!\nНапомню, что прошла уже половина подписки. 🤓\n" \
        "#ВремяЛетит"
    FIVE = "Hi, дорогой пользователь!\n" \
        "Срок действия твоей подписки закончится через 5 дней.\n" \
        "Отложи деньги на оформление новой заранее. 🤑\n" \
        "#ЭтоПросто"
    ONE = "Hi, дорогой пользователь!\n" \
        "Срок действия твоей подписки закончится уже завтра\n" \
        "Приготовься оформить новую подписку. 💳\n" \
        "#ЭтоУдобно"
