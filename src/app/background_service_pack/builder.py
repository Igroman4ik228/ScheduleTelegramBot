from app.background_service_pack.models import BackgroundService
from app.factory_pack.models import IBackgroundServiceFactory
from app.factory_pack.parser_factory import ParserFactory
from services.sub_checker_service.sub_checker import SubCheckerService


class BackgroundBuilder:
    def __init__(self, parser_factory: ParserFactory, sub_checker: SubCheckerService):
        self.installation_service = [parser_factory, sub_checker]

    def get_services(self) -> list[BackgroundService]:
        services: list[BackgroundService] = []
        for app in self.installation_service:
            if isinstance(app, IBackgroundServiceFactory):
                getter_services = app.get()
                for getter_service in getter_services:
                    services.append(getter_service)
            else:
                services.append(app)

        return services
