import asyncio
from logging import Logger

from aiohttp import ClientError, ClientResponseError, ClientSession


def retry_request(func):

    async def wrapper(self, *args, **kwargs):
        for seconds in [15, 30, 60]:
            try:
                return await func(self, *args, **kwargs)
            except (ClientResponseError, ClientError):
                self.logger.error("Не удалось подключиться к сайту. "
                                  f"Повторная попытка через {seconds} секунд.")
                await asyncio.sleep(seconds)
        return await func(self, *args, **kwargs)
    return wrapper


class Request():
    def __init__(self, url: str, logger: Logger) -> None:
        self.url = url
        self.logger = logger

    @retry_request
    async def fetch(self) -> str:
        async with ClientSession() as session:
            async with session.get(self.url, timeout=20) as response:
                response.raise_for_status()
                return await response.text()
