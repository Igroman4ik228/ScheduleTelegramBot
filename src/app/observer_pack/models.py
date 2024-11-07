import asyncio
import logging
from abc import ABC, abstractmethod


class Observer(ABC):

    @abstractmethod
    async def update(self) -> None:
        pass


class Publisher(ABC):

    @abstractmethod
    def __init__(self) -> None:
        self.services: list[Observer] = []
        self.is_update: bool = False
        self.logger = logging.getLogger(__class__.__name__)

    def attach(self, observer: Observer) -> None:
        self.services.append(observer)

    def detach(self, observer: Observer) -> None:
        self.services.remove(observer)

    async def notify(self) -> None:
        if self.is_update:
            await asyncio.gather(*(service.update() for service in self.services))
            self.is_update = False
