
from abc import ABC, abstractmethod

from app.background_service_pack.models import BackgroundService

class IBackgroundServiceFactory(ABC):
    def __init__(self, additional_param: list[object], time_span: int):
        self.additional_param = additional_param
        self.time_span = time_span

    def get(self) -> (list[BackgroundService] | None):
        if self.additional_param.count == 0:
            return None
        elif self.additional_param.count == 1:
            return self._create()
        else:
            return self._create_range()

    @abstractmethod
    def _create(self) -> BackgroundService:
        pass

    @abstractmethod
    def _create_range(self) -> list[BackgroundService]:
        pass
