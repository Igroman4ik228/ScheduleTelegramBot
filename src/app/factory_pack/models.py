
from abc import ABC, abstractmethod

from app.background_service_pack.models import BackgroundService


class IBackgroundServiceFactory(ABC):
    def __init__(self, time_span: int):
        self.time_span = time_span

    def get(self) -> (list[BackgroundService] | None):
        return self._create()

    @abstractmethod
    def _create(self) -> list[BackgroundService]:
        pass
