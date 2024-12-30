import asyncio
from abc import ABC, abstractmethod
from logging import getLogger


class BackgroundService(ABC):
    @abstractmethod
    def __init__(self, time_span: int) -> None:
        '''
        args:
            time_span - in second
        '''
        self.logger = getLogger(self.__class__.__name__)
        self.is_active: bool = False
        self.time_span = time_span

    @abstractmethod
    async def do_work(self):
        pass

    async def active(self):
        self.is_active = True
        while self.is_active:
            await self.do_work()
            await asyncio.sleep(self.time_span)

    async def pause(self):
        self.is_active = False

    @abstractmethod
    async def stop(self):
        pass
