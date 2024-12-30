import asyncio
from datetime import timedelta
from functools import wraps
from logging import getLogger

from aiohttp import (ClientError, ClientResponseError, ClientSession,
                     ClientTimeout)

DEFAULT_TIMEOUT = timedelta(seconds=10).seconds
# DEFAULT_HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
# }
DEFAULT_RETRY_DELAYS = [
    timedelta(seconds=10).seconds,
    timedelta(seconds=30).seconds,
    timedelta(seconds=60).seconds
]


def retry_request(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        for seconds in self.retry_delays:
            try:
                return await func(self, *args, **kwargs)
            except (ClientResponseError, ClientError) as e:
                self.logger.error(
                    f"Ошибка подключения к {self.url}: {e}. "
                    f"Повторная попытка через {seconds} секунд."
                )
                await asyncio.sleep(seconds)
        return await func(self, *args, **kwargs)
    return wrapper


class Request:
    def __init__(
        self,
        url: str,
        timeout: int = DEFAULT_TIMEOUT,
        retry_delays: list[int] = None,
        headers: dict[str, str] = None
    ) -> None:
        self.logger = getLogger(self.__class__.__name__)
        self.url = url
        self.timeout = timeout
        self.retry_delays = retry_delays or DEFAULT_RETRY_DELAYS
        self.headers = headers

    @retry_request
    async def fetch(self) -> str:
        timeout = ClientTimeout(total=self.timeout)
        async with ClientSession() as session:
            async with session.get(self.url, timeout=timeout) as response:
                response.raise_for_status()
                return await response.text()
