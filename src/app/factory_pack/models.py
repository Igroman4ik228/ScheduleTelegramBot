from abc import ABC, abstractmethod

from app.background_service_pack.models import BackgroundService


class BackgroundServiceFactory(ABC):
    def get(self) -> list[BackgroundService]:
        return self._create()

    @abstractmethod
    def _create(self) -> list[BackgroundService]: ...
