import asyncio
from datetime import timedelta
from functools import wraps
from logging import getLogger

from aiohttp import ClientError, ClientResponseError, ClientSession

from services.sender_service.sender import SenderService

DEFAULT_TIMEOUT = timedelta(seconds=10).seconds
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
DEFAULT_RETRY_DELAYS = [
    timedelta(seconds=10).seconds,
    timedelta(seconds=30).seconds,
    timedelta(seconds=60).seconds,
]


def retry_request(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        for seconds in self.retry_delays:
            try:
                return await func(self, *args, **kwargs)
            except (ClientResponseError, ClientError) as e:
                self.logger.warning(
                    f"Ошибка подключения: {e}. "
                    f"Повторная попытка через {seconds} секунд."
                )
                await asyncio.sleep(seconds)

        await self.sender.safe_send_range(
            self.admin_ids,
            f"Ошибка подключения к {self.url}\nбудут продолжаться повторные попытки",
        )

        # Бесконечные попытки
        while True:
            try:
                result = await func(self, *args, **kwargs)
                await self.sender.safe_send_range(
                    self.admin_ids, "Подключение восстановлено"
                )
                return result
            except (ClientResponseError, ClientError) as e:
                self.logger.warning(
                    f"Ошибка подключения к {self.url}: {e}. "
                    f"Повторная попытка через {self.retry_delays[-1]} секунд."
                )
                await asyncio.sleep(self.retry_delays[-1])

    return wrapper


class Request:
    def __init__(
        self,
        admin_ids: list[int],
        sender: SenderService,
        timeout: int = DEFAULT_TIMEOUT,
        retry_delays: list[int] = None,
        headers: dict[str, str] = None,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.admin_ids = admin_ids
        self.sender = sender
        self.timeout = timeout
        self.retry_delays = retry_delays or DEFAULT_RETRY_DELAYS
        self.headers = headers or DEFAULT_HEADERS

    @retry_request
    async def fetch(self, url) -> str:
        async with ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.text()
