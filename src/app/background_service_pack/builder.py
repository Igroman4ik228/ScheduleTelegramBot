from app.background_service_pack.models import BackgroundService
from app.factory_pack.models import BackgroundServiceFactory


class BackgroundBuilder:
    def __init__(self, *services: BackgroundService | BackgroundServiceFactory):
        self._services = services

    def get_services(self) -> list[BackgroundService]:
        services: list[BackgroundService] = []
        for service in self._services:
            if isinstance(service, BackgroundServiceFactory):
                services.extend(service.get())
            else:
                services.append(service)
        return services
