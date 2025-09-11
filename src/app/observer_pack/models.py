import asyncio
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    async def update(self, *args, **kwargs): ...


class Publisher(ABC):
    @abstractmethod
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify(self, *args, **kwargs):
        if self._observers:
            await asyncio.gather(
                *(
                    observer.update(*args, **kwargs)
                    for observer in self._observers
                )
            )
