from abc import ABC, abstractmethod
import asyncio
from logging import Logger


class Observer(ABC):

    @abstractmethod
    async def update(self) -> None:
        pass


class Publisher(ABC):

    @abstractmethod
    def __init__(self, logger: Logger) -> None:
        self.services: list[Observer] = []
        self.is_update: bool = False
        self.logger = logger

    def attach(self, observer: Observer) -> None:
        self.services.append(observer)

    def detach(self, observer: Observer) -> None:
        self.services.remove(observer)

    async def notify(self) -> None:
        self.logger.info("Start of notify")
        if self.is_update:
            await asyncio.gather(*(service.update() for service in self.services))
            self.logger.info("End of notify")
            self.is_update = False
