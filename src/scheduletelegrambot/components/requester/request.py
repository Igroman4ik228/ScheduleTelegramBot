import asyncio
from datetime import timedelta
from functools import wraps
from logging import getLogger
from typing import TYPE_CHECKING

from aiohttp import ClientError, ClientResponseError, ClientSession

if TYPE_CHECKING:
    from scheduletelegrambot.components.sender.sender import TelegramSender

DEFAULT_TIMEOUT = timedelta(seconds=10).seconds
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
            except (ClientResponseError, ClientError) as error:
                self.logger.warning(
                    "Connection error: %s. Retrying in %s seconds.",
                    error,
                    seconds,
                )
                await asyncio.sleep(seconds)

        await self.sender.safe_send_range(
            self.admin_ids,
            f"Connection to {self.url} failed; retries will continue.",
        )

        # Бесконечные попытки
        while True:
            try:
                result = await func(self, *args, **kwargs)
                await self.sender.safe_send_range(self.admin_ids, "Подключение восстановлено")
            except (ClientResponseError, ClientError) as error:
                self.logger.warning(
                    "Connection to %s failed: %s. Retrying in %s seconds.",
                    self.url,
                    error,
                    self.retry_delays[-1],
                )
                await asyncio.sleep(self.retry_delays[-1])
            else:
                await self.sender.safe_send_range(self.admin_ids, "Подключение восстановлено")
                return result

    return wrapper


class AdminRequester:
    def __init__(
        self,
        admin_ids: list[int],
        sender: TelegramSender,
        timeout: int = DEFAULT_TIMEOUT,
        retry_delays: list[int] | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.admin_ids = admin_ids
        self.sender = sender
        self.timeout = timeout
        self.retry_delays = retry_delays or DEFAULT_RETRY_DELAYS
        self.headers = headers or DEFAULT_HEADERS

    @retry_request
    async def fetch(self, url: str) -> str:
        async with ClientSession() as session, session.get(url, headers=self.headers) as response:
            response.raise_for_status()
            return await response.text()
