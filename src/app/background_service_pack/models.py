import asyncio
from abc import ABC, abstractmethod
from contextlib import suppress
from logging import getLogger


class BackgroundService(ABC):
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._running: bool = False

    @abstractmethod
    async def do_work(self): ...

    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._runner())

    async def pause(self):
        self._running = False

    async def stop(self):
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._task = None

    @abstractmethod
    async def _runner(self): ...


class IntervalService(BackgroundService):
    def __init__(self, interval: int):
        super().__init__()
        self.logger = getLogger(self.__class__.__name__)
        self.interval = interval

    async def _runner(self):
        try:
            while self._running:
                await self.do_work()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            self.logger.info("Service cancelled")
